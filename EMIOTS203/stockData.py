import base64
from io import BytesIO
import datetime
import os

import pandas as pd
import yfinance as yf
from matplotlib.figure import Figure

# setting up django for script testing, uncomment lines below to sun tests
# import sys
# import django
# thisFilePath = os.path.dirname(__file__)
# rootLocation = os.path.abspath(os.path.join(thisFilePath, ".."))
# sys.path.append(rootLocation)
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
# django.setup()

from EMIOTS203.models import Tweet, StockChart


class StockData:
    def __init__(self, *args, **kwargs):
        self.ticker = "TSLA"
        self.interval = '5m'
        self.stockData = pd.DataFrame()
        self.tweetsDates = pd.DataFrame()

    # Converting figure in .png format to base64
    def _getB64HtmlFromChart(self, figure):
        buf = BytesIO()
        figure.savefig(buf, format="png")
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        htmlContent = f"<img src='data:image/png;base64,{data}'/>"

        return htmlContent

    #  Plotting charts
    def _plottingTheFigure(self, indexValues, openValues, tweetTime, minValue, maxValue, volumeValues, openingDate,
                           closingDate):
        fig = Figure(figsize=(16, 8))
        ax = fig.add_subplot(111)

        if openingDate != closingDate:
            ax.set_title(str(openingDate) + " - " + str(closingDate))
        else:
            ax.set_title(str(openingDate))

        # ax.set_xlabel("Time of tweet")
        ax.set_ylabel("Price")
        ax.tick_params(axis='x', length=2, pad=2, labelsize=7, labelrotation=85, labelleft=True)

        stockPrice, = ax.plot(indexValues, openValues, 'r-', label="Stock price", color='r', lw=3)
        tweetDate, = ax.plot([tweetTime, tweetTime], [minValue, maxValue], 'k--', lw=3)

        ax2 = ax.twinx()
        ax2.set_ylabel("Volume")
        stockVolume, = ax2.plot(indexValues, volumeValues, 'r-', label="Volume", color='b', lw=3)

        ax.legend(handles=[stockPrice, tweetDate, stockVolume],
                  labels=["Stock price", "Tweet date", "Stock volume"],
                  loc="upper left")
        return fig

    # Analysing stock data and tweets
    def _analysingStockData(self, x, idx, stockData, tweets):
        firstHour = stockData.iloc[idx:idx+13]  # collecting data from first hour after tweet
        firstHourHighestPeak = firstHour["High"].max()  # finding max stock price
        firstHourLowestPeak = firstHour["Low"].min()    # finding min stock price
        openingValue = firstHour["Open"][0]

        swingInPlus = (firstHourHighestPeak - openingValue)/openingValue*100    # calculating swing in plus
        swingInMinus = (firstHourLowestPeak - openingValue)/openingValue*100    # calculating swing in minus

        threeHoursBefore = stockData.iloc[idx-36: idx+1]
        openingDate = threeHoursBefore.index[0].strftime('%Y-%m-%d')
        threeHoursBefore.index = threeHoursBefore.index.format(formatter=lambda x: x.strftime('%H:%M'))

        threeHoursAfter = stockData.iloc[idx+1: idx+37]
        closingDate = threeHoursAfter.index[-1].strftime('%Y-%m-%d')
        threeHoursAfter.index = threeHoursAfter.index.format(formatter=lambda x: x.strftime('%H:%M'))

        tweetTimeIdx = tweets.iloc[x, 0].strftime('%m-%d %H:%M')
        tweetTime = pd.DataFrame(data=None, columns=threeHoursBefore.columns, index=[tweetTimeIdx])

        sixHoursSpan = pd.concat([threeHoursBefore, tweetTime, threeHoursAfter])

        minIn6Hours = sixHoursSpan["Open"].min()
        maxIn6Hours = sixHoursSpan["Open"].max()

        tweetExactTime = sixHoursSpan.index[sixHoursSpan.index.get_loc(key=tweetTimeIdx)]

        if abs(swingInMinus) > swingInPlus:
            maxSwing = swingInMinus
        else:
            maxSwing = swingInPlus

        return sixHoursSpan, tweetExactTime, minIn6Hours, maxIn6Hours, maxSwing, openingDate, closingDate

    # Correlating stock data with tweets
    def comparingTweetsWithStock(self):
        allTweets = Tweet.objects.all()
        tweetsWithoutStockchart = allTweets.filter(stockchart__isnull=True)
        startDate = (tweetsWithoutStockchart.earliest('date').date + datetime.timedelta(-1)).strftime('%Y-%m-%d')
        endDate = datetime.date.today().strftime('%Y-%m-%d')

        self.stockData = yf.download(self.ticker,
                                     start=startDate,
                                     end=endDate,
                                     interval=self.interval,
                                     progress=False)

        self.stockData.index = pd.to_datetime(self.stockData.index, format='%Y-%m-%d %H:%M:%S', utc='US/Eastern')
        self.tweets = pd.DataFrame(list(tweetsWithoutStockchart.values('date', 'externalId')))

        chartCounter = 0

        for x in range(self.tweets.shape[0]):
            idx = self.stockData.index.get_loc(key=self.tweets.iloc[x, 0], method='pad')
            tweetId = self.tweets.iloc[x, 1]

            tweetAnalysis = self._analysingStockData(x, idx, self.stockData, self.tweets)
            sixHoursSpan = tweetAnalysis[0]
            tweetExactTime = tweetAnalysis[1]
            minIn6Hours = tweetAnalysis[2]
            maxIn6Hours = tweetAnalysis[3]
            maxSwing = tweetAnalysis[4]
            openingDate = tweetAnalysis[5]
            closingDate = tweetAnalysis[6]

            fig = self._plottingTheFigure(sixHoursSpan.index, sixHoursSpan["Open"], tweetExactTime, minIn6Hours,
                                          maxIn6Hours, sixHoursSpan["Volume"], openingDate, closingDate)

            chartHtml = self._getB64HtmlFromChart(fig)

            StockChart.objects.create(chartHtml=chartHtml,
                                      maxSwing=maxSwing,
                                      tweetId=Tweet.objects.get(pk=tweetId))
            chartCounter += 1
        print(f"{chartCounter} stockcharts were added to database")

    # Adding stockcharts based on csv file
    def migrateStockFromCsvToDatabase(self):
        thisFilePath = os.path.dirname(__file__)
        stockFileName = 'stock_data.csv'
        stockFileName = os.path.abspath(os.path.join(thisFilePath, "..", "data", stockFileName))

        allTweets = Tweet.objects.all()
        tweetsWithoutStockchart = allTweets.filter(stockchart__isnull=True)
        self.tweets = pd.DataFrame(list(tweetsWithoutStockchart.values('date', 'externalId')))

        self.stockData = pd.read_csv(stockFileName, index_col=0)
        self.stockData.index = pd.to_datetime(self.stockData.index, format='%Y-%m-%d %H:%M:%S', utc='US/Eastern')

        chartCounter = 0

        for x in range(self.tweets.shape[0]):
            idx = self.stockData.index.get_loc(key=self.tweets.iloc[x, 0], method='pad')
            tweetId = self.tweets.iloc[x, 1]

            tweetAnalysis = self._analysingStockData(x, idx, self.stockData, self.tweets)
            sixHoursSpan = tweetAnalysis[0]
            tweetExactTime = tweetAnalysis[1]
            minIn6Hours = tweetAnalysis[2]
            maxIn6Hours = tweetAnalysis[3]
            maxSwing = tweetAnalysis[4]
            openingDate = tweetAnalysis[5]
            closingDate = tweetAnalysis[6]

            fig = self._plottingTheFigure(sixHoursSpan.index, sixHoursSpan["Open"], tweetExactTime, minIn6Hours,
                                          maxIn6Hours, sixHoursSpan["Volume"], openingDate, closingDate)

            chartHtml = self._getB64HtmlFromChart(fig)

            StockChart.objects.create(chartHtml=chartHtml,
                                      maxSwing=maxSwing,
                                      tweetId=Tweet.objects.get(pk=tweetId))
            chartCounter += 1

        print(f"{chartCounter} stockcharts were added to database")


# TODO: zakomentowanie maina i nagłówka, żeby sobie testować
if __name__ == '__main__':
    stock = StockData()
    stock.comparingTweetsWithStock()
