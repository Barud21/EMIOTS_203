from periodic.celery import app

from tweetsFetcher import TweetsFetcher


@app.task
def check():
    print('I am a test task!')


@app.task
def createOrUpdateTweetsDataFile():
    fetcher = TweetsFetcher(username='elonmusk', companyOfInterest='Tesla')
    fetcher.createOrUpdateDataFile()
