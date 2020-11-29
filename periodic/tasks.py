from periodic.celery import app

from EMIOTS203.tweetsFetcher import TweetsFetcher


@app.task
def check():
    print('I am a test task!')


@app.task
def createOrUpdateTweetsDb():
    fetcher = TweetsFetcher(username='elonmusk', companyOfInterest='Tesla')

    # rerurns list of dicts with basic info about new important tweets - published date and html element
    fetcher.createOrUpdateDb()
