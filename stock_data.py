import csv
import pandas as pd
import yfinance as yf
from yahoofinancials import YahooFinancials
import datetime
import os.path
from os import path
import dateutil
import pytz


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
        if path.exists('ndata.csv'):
            self.data = pd.read_csv('ndata.csv', index_col=0)    # index_col = 0 guarantees, that the index column is filled with datetime, pandas read_csv always adds index column (0, 1, ...)
            last_date = self.data.index[-1]                     # accessing the last index value
            last_date = last_date[0:10]                         # taking only date form datetime index
            start_date = (datetime.datetime.strptime(last_date, '%Y-%m-%d').date() + datetime.timedelta(2)).strftime('%Y-%m-%d')    # defining the start date for our request
            daysDifference = (datetime.date.today() - datetime.datetime.strptime(last_date, '%Y-%m-%d').date()).days    # calculating the days difference between today and last date in file

            print(daysDifference)
            print(last_date)
            print(datetime.date.today())

            if daysDifference < 2:
                print("Data is up to date")

            elif 1 < daysDifference < 60:
                last60Days = yf.download(  self.ticker,
                                            start=start_date,
                                            end=datetime.date.today().strftime('%Y-%m-%d'),
                                            interval=self.interval,
                                            progress=False
                )

                print(self.data)
                print(last60Days)

                concatData = pd.concat([self.data, last60Days])
                concatData.to_csv('ndata.csv')
                print(concatData)

            elif daysDifference > 59:
                daysDifference = daysDifference-61
                daysDifference = int(daysDifference)
                historicEndDate = (datetime.datetime.strptime(start_date, '%Y-%m-%d').date() + datetime.timedelta(daysDifference)).strftime('%Y-%m-%d')

                historicData = yf.download( self.ticker,
                                            start=start_date,
                                            end=historicEndDate,
                                            interval='1d',
                                            progress=False
                )
                
                last60Days = yf.download(  self.ticker,
                                            start = (datetime.date.today() + datetime.timedelta(-59)).strftime('%Y-%m-%d'),
                                            end=datetime.date.today(),
                                            interval='5m',
                                            progress=False
                )

                concatData = pd.concat([self.data, historicData])
                concatData = pd.concat([concatData, last60Days])
                concatData.to_csv('ndata.csv')

    
    def downloadingDataFirstTime(self):
        if path.isfile('ndata.csv') == False:
            historicData = yf.download( self.ticker,
                                        start='2017-01-01',
                                        end=(datetime.date.today() + datetime.timedelta(-59)).strftime('%Y-%m-%d'),
                                        interval='1d',
                                        progress=False
            )

            last60Days = yf.download(   self.ticker,
                                        start=(datetime.date.today() + datetime.timedelta(-59)).strftime('%Y-%m-%d'),
                                        end=datetime.date.today().strftime('%Y-%m-%d'),
                                        interval='5m',
                                        progress=False
            )

            concatData = pd.concat([historicData, last60Days])
            concatData.to_csv('ndata.csv')
            # print(historicData)
            # print(last60Days)
            # print(concatData)

    def extractingTweetsDates(self):
        self.tweets = pd.read_csv('elonmusk_Tweets.csv', index_col=0)
        print(self.tweets)
        
        self.tweetsDates = self.tweets.iloc[:, 0:1]
        print(self.tweetsDates)

        self.data.index = pd.to_datetime(self.data.index, format='%Y-%m-%d %H:%M:%S', utc='US/Eastern')
        print(self.data.index)

        print(self.tweetsDates.iloc[0,0])

        idx = [str(self.data.index[self.data.index.get_loc(key=self.tweetsDates.iloc[x, 0], method='nearest')]) for x in range(self.tweetsDates.size)]    
        
        print(idx)


if __name__ == '__main__':
    stock = StockData()
    stock.updatingStockData()
    # stock.downloadingDataFirstTime()
    stock.extractingTweetsDates()
