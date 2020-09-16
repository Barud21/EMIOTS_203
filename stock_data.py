import csv
import pandas as pd
import yfinance as yf
from yahoofinancials import YahooFinancials
import datetime
import os.path
from os import path


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
    
    def updatingStockData(self):
        if path.exists('concat.csv'):
            dataFile = pd.read_csv('concat.csv')
            last_date = dataFile.iloc[-1][0]
            last_date = last_date[0:10]
            start_date = (datetime.datetime.strptime(last_date, '%Y-%m-%d').date() + datetime.timedelta(1)).strftime('%Y-%m-%d')
            # daysDifference = (datetime.date.today() - last_date).days
            
            print(last_date)
            print(datetime.date.today())
            # print(daysDifference)
            updatedData = yf.download(  self.ticker,
                                        start=start_date,
                                        end=datetime.date.today().strftime('%Y-%m-%d'),
                                        interval=self.interval,
                                        progress=False
            )
            print(updatedData)
    
    def savingStockData(self):
        if path.exists('concat.csv'):
            dataFile = pd.read_csv('concat.csv')
            bottom_row = dataFile.tail(1)
            last_date = bottom_row.iloc[0]['Datetime']
            location = self.data.index.get_loc(last_date)
            print(location)
            
            newData = self.data.truncate(before=last_date)
            newData = newData.drop(newData.index[[0]])
            print(newData)
            concatData = pd.concat([self.data, newData])
            concatData.to_csv('concat.csv')
            
        else:
            self.data.to_csv('concat.csv')
    
    def gettingHistoricalData(self):
        self.historic = yf.download(self.ticker,
                                    start='2017-01-01',
                                    end='2020-07-14',
                                    interval='1d',
                                    progress=False
                                    )
        self.historic.to_csv('historic.csv')


if __name__ == '__main__':
    stock = StockData()
    stock.updatingStockData()