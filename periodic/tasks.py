from datetime import datetime, timezone

from periodic.celery import app

from tweetsFetcher import TweetsFetcher
from EMIOTS203.models import TweetAndStockChart


@app.task
def check():
    print('I am a test task!')


@app.task
def createOrUpdateTweetsDataFile():
    fetcher = TweetsFetcher(username='elonmusk', companyOfInterest='Tesla')

    # rerurns list of dicts with basic info about new important tweets - published date and html element
    fetcher.createOrUpdateDataFile()


# a placeholder code for future reference
# shows how to create an object in db using Django model
# @app.task
def testDb():
    print('Creating a db object')
    TweetAndStockChart.objects.create(tweetHtmlContent='testTweetContent',
                                      chartHtmlContent='testChartContent',
                                      maxStockChange=-2,
                                      publish_date=datetime.now(timezone.utc))
