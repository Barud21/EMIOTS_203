from periodic.celery import app

from EMIOTS203.tweetsFetcher import TweetsFetcher
from EMIOTS203.stockData import StockData


@app.task
def check():
    print('I am a test task!')


@app.task
def createOrUpdateDb():
    fetcher = TweetsFetcher(username='elonmusk', companyOfInterest='Tesla')

    fetcher.createOrUpdateDb()

    stockchart = StockData()
    stockchart.comparingTweetsWithStock()
