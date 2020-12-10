import datetime
from os import path

import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import mpld3


class StockData:
    def __init__(self, *args, **kwargs):
        self.startDate = '2020-07-29'
        self.endDate = '2020-09-05'
        self.date = datetime.date.today().strftime('%Y-%m-%d')
        self.date_60 = (datetime.date.today() + datetime.timedelta(-59)).strftime('%Y-%m-%d')
        self.interval = '5m'
        self.ticker = "TSLA"
        self.data = pd.DataFrame()
        self.historic = pd.DataFrame()
        self.tweets = pd.DataFrame()
        self.tweetsDates = pd.DataFrame()

    def updatingStockData(self):
        if path.exists('data/stock_data.csv'):
            self.data = pd.read_csv('data/stock_data.csv', index_col=0)      # index_col = 0 guarantees, that the index
            # column is filled with datetime, pandas read_csv always adds index column (0, 1, ...)
            last_date = self.data.index[-1]                     # accessing the last index value
            last_date = last_date[0:10]                         # taking only date form datetime index
            start_date = (datetime.datetime.strptime(last_date, '%Y-%m-%d').date() +
                          datetime.timedelta(2)).strftime('%Y-%m-%d')    # defining the start date for our request
            daysDifference = (datetime.date.today() - datetime.datetime.strptime(last_date, '%Y-%m-%d').date()).days
            # calculating the days difference between today and last date in file

            print(daysDifference)
            print(last_date)
            print(datetime.date.today())

            if daysDifference < 2:
                print("Data is up to date")

            elif 1 < daysDifference < 60:
                last60Days = yf.download(self.ticker,
                                         start=start_date,
                                         end=datetime.date.today().strftime('%Y-%m-%d'),
                                         interval=self.interval,
                                         progress=False)

                print(self.data)
                print(last60Days)

                concatData = pd.concat([self.data, last60Days])
                concatData.to_csv('data/stock_data.csv')
                print(concatData)

            elif daysDifference > 59:
                daysDifference = daysDifference-61
                daysDifference = int(daysDifference)
                historicEndDate = (datetime.datetime.strptime(start_date, '%Y-%m-%d').date() +
                                   datetime.timedelta(daysDifference)).strftime('%Y-%m-%d')

                historicData = yf.download(self.ticker,
                                           start=start_date,
                                           end=historicEndDate,
                                           interval='1d',
                                           progress=False)

                last60Days = yf.download(self.ticker,
                                         start=(datetime.date.today() + datetime.timedelta(-59)).strftime('%Y-%m-%d'),
                                         end=datetime.date.today(),
                                         interval='5m',
                                         progress=False)

                concatData = pd.concat([self.data, historicData])
                concatData = pd.concat([concatData, last60Days])
                concatData.to_csv('data/stock_data.csv')

    def downloadingDataFirstTime(self):
        if path.isfile('data/stock_data.csv') is False:
            historicData = yf.download(self.ticker,
                                       start='2017-01-01',
                                       end=(datetime.date.today() + datetime.timedelta(-59)).strftime('%Y-%m-%d'),
                                       interval='1d',
                                       progress=False)

            last60Days = yf.download(self.ticker,
                                     start=(datetime.date.today() + datetime.timedelta(-59)).strftime('%Y-%m-%d'),
                                     end=datetime.date.today().strftime('%Y-%m-%d'),
                                     interval='5m',
                                     progress=False)

            concatData = pd.concat([historicData, last60Days])
            concatData.to_csv('data/stock_data.csv')

    def extractingTweetsDates(self):
        self.tweets = pd.read_csv('data/elonmusk_Tweets.csv', index_col=0)
        # print(self.tweets)

        self.tweetsDates = self.tweets.iloc[:, 0:1]
        # print(self.tweetsDates)

        self.data.index = pd.to_datetime(self.data.index, format='%Y-%m-%d %H:%M:%S', utc='US/Eastern')
        # print(self.data.index)

        # print(self.tweetsDates.iloc[0, 0])
        print('***************')

        for x in range(-3, -1):   # self.tweets.shape[0]
            print(self.tweets.iloc[x, 0])
            idx = self.data.index.get_loc(key=self.tweetsDates.iloc[x, 0], method='pad')    # finding last stock
            # price before tweet

            firstHour = self.data.iloc[idx:idx+13]  # collecting data from first hour after tweet
            firstHourHighestPeak = firstHour["High"].max()  # finding max stock price
            firstHourLowestPeak = firstHour["Low"].min()    # finding min stock price
            openingValue = firstHour["Open"][0]

            swingInPlus = (firstHourHighestPeak - openingValue)/openingValue*100    # calculating swing in plus
            swingInMinus = (firstHourLowestPeak - openingValue)/openingValue*100    # calculating swing in minus

            threeHoursBefore = self.data.iloc[idx-36: idx+1]
            threeHoursBefore.index = threeHoursBefore.index.format(formatter=lambda x: x.strftime('%H:%M'))

            threeHoursAfter = self.data.iloc[idx+1: idx+37]
            threeHoursAfter.index = threeHoursAfter.index.format(formatter=lambda x: x.strftime('%H:%M'))

            # TODO: create tmp for this and 2nd line of for
            tweetTimeIdx = datetime.datetime.strptime(self.tweets.iloc[x, 0], '%Y-%m-%d %H:%M:%S')
            tweetTimeIdx = tweetTimeIdx.strftime('%m-%d %H:%M')
            tweetTime = pd.DataFrame(data=None, columns=threeHoursBefore.columns, index=[tweetTimeIdx])

            # tweetTime["Open"][0] = (threeHoursBefore["Open"][-1] + threeHoursAfter["Open"][0])/2
            # tweetTime["Volume"][0] = (threeHoursBefore["Volume"][-1] + threeHoursAfter["Volume"][0])/2

            sixHoursSpan = pd.concat([threeHoursBefore, tweetTime, threeHoursAfter])

            minIn6Hours = sixHoursSpan["Open"].min()
            maxIn6Hours = sixHoursSpan["Open"].max()

            # --------first option--------
            fig = plt.figure(figsize=(16, 9))
            ax = fig.add_subplot(111)
            ax.set_title("EMIOTS")
            ax.set_xlabel("Time")
            ax.set_ylabel("Price")
            # plt.xticks(rotation=45)
            ax.tick_params(axis='x', length=2, pad=2, labelsize=7, labelrotation=85, labelleft=True)
            # ax.set_view_interval()

            ax.plot(sixHoursSpan.index, sixHoursSpan["Open"], 'r-', label="Stock price", lw=4)
            ax.plot([sixHoursSpan.index[sixHoursSpan.index.get_loc(key=tweetTimeIdx)],
                    sixHoursSpan.index[sixHoursSpan.index.get_loc(key=tweetTimeIdx)]], [minIn6Hours, maxIn6Hours],
                    'k--', lw=3)

            ax2 = ax.twinx()
            ax2.set_ylabel("Volume")
            ax2.plot(sixHoursSpan.index, sixHoursSpan["Volume"], 'b-', label="Volume", lw=4)

            mpld3.fig_to_html(fig)
            plt.show()
            fig.savefig('my_plot.png')
            mpld3.save_html(fig, "figure.html")

            # --------second option--------
            # plt.figure(figsize=(8, 5))
            # sixHoursSpan["Open"].plot(legend=True, grid=True, title="EMIOTS", ylabel="Stock price", xlabel="Time")
            # plt.xticks()
            # sixHoursSpan["Volume"].plot(secondary_y=True, legend=True, grid=True)
            # plt.show()
            # plt.xticks(range(0, len(sixHoursSpan.index)), sixHoursSpan.index)

            print(idx)
            print(openingValue)
            print(firstHour)
            print("")
            print(firstHourHighestPeak)
            print("")
            print(firstHourLowestPeak)
            print("")
            print(swingInPlus)
            print("")
            print(swingInMinus)
            print("")
            pd.set_option('display.max_rows', None)
            print(sixHoursSpan)
            print("")
            # plt.show()


if __name__ == '__main__':
    stock = StockData()
    stock.updatingStockData()
    # stock.downloadingDataFirstTime()
    stock.extractingTweetsDates()
