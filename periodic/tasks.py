from periodic.celery import app

from EMIOTS203.tweetsFetcher import TweetsFetcher
from EMIOTS203.stockData import StockData
from EMIOTS203.models import Tweet

import datetime


@app.task
def check():
    print('I am a test task!')


@app.task
def createOrUpdateDb():
    fetcher = TweetsFetcher(username='elonmusk', companyOfInterest='Tesla')

    fetcher.createOrUpdateDb()

    stockchart = StockData()
    stockchart.comparingTweetsWithStock()


@app.task
def removeOldTweetsWithoutStockCharts():
    borderDate = datetime.datetime.utcnow() - datetime.timedelta(weeks=4)
    borderDate = borderDate.replace(tzinfo=datetime.timezone.utc)

    qs = Tweet.objects.filter(stockchart__isnull=True, date__lte=borderDate)
    qs.delete()
