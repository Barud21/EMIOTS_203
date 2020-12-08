from periodic.celery import app

from EMIOTS203.tweetsFetcher import TweetsFetcher


@app.task
def check():
    print('I am a test task!')


@app.task
def createOrUpdateTweetsDb():
    fetcher = TweetsFetcher(username='elonmusk', companyOfInterest='Tesla')

    fetcher.createOrUpdateDb()
