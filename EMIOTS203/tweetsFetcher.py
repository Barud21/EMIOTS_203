import csv
import os
import re
import datetime

import tweepy
import requests

from .models import Tweet

from project.settings import (TWEETSFETCHER_CUSTOMERKEY,
                              TWEETSFETCHER_CUSTOMERSECRET,
                              TWEETSFETCHER_ACCESSTOKEN,
                              TWEETSFETCHER_ACCESSTOKENSECRET)


class TweetsFetcher:
    def __init__(self, username, companyOfInterest):
        self.customer_key = TWEETSFETCHER_CUSTOMERKEY
        self.customer_secret = TWEETSFETCHER_CUSTOMERSECRET
        self.access_token = TWEETSFETCHER_ACCESSTOKEN
        self.access_token_secret = TWEETSFETCHER_ACCESSTOKENSECRET

        self.userId = username
        self.companyOfInterest = companyOfInterest

        # 60, as for this period we can get detailed stock data
        self.maxDaysAgoToFetchTweets = 60

        self.api = self._authorizeMe()

    def _authorizeMe(self):
        auth = tweepy.OAuthHandler(self.customer_key, self.customer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        api = tweepy.API(auth)
        return api

    # give it list of tweetStatus objects from API and a datetime
    # it will return these tweets which are younger than a given datetime
    def _filterTweetsYoungerThanDateTimeLimit(self, tweetsList, datetimeLimit):
        filteredTweets = []

        if len(tweetsList) > 0:
            oldestTweetDatetimeTzAware = tweetsList[-1].created_at.replace(tzinfo=datetime.timezone.utc)

            if oldestTweetDatetimeTzAware < datetimeLimit:
                for tweetStatus in tweetsList:
                    tweetDateTimeTzAware = tweetStatus.created_at.replace(tzinfo=datetime.timezone.utc)
                    if tweetDateTimeTzAware > datetimeLimit:
                        filteredTweets.append(tweetStatus)
                    else:
                        continue
            else:
                filteredTweets.extend(tweetsList)

        return filteredTweets

    def _getAllTweetsThatArePossibleToFetch(self):
        allTweets = []
        TweetsPerRequestMax = 200  # max allowed
        tweetsBatch = self.api.user_timeline(screen_name=self.userId,
                                             tweet_mode='extended',
                                             count=TweetsPerRequestMax
                                             )

        datetimeLimit = datetime.datetime.now(datetime.timezone.utc) - \
            datetime.timedelta(days=self.maxDaysAgoToFetchTweets)

        if len(tweetsBatch) > 0:
            print('The oldest tweet fetched from API (no filter) has the following date ', tweetsBatch[-1].created_at)

            filteredTweets = self._filterTweetsYoungerThanDateTimeLimit(tweetsList=tweetsBatch,
                                                                        datetimeLimit=datetimeLimit)
            allTweets.extend(filteredTweets)
            oldestTweetDateTime = filteredTweets[-1].created_at.replace(tzinfo=datetime.timezone.utc)

            if oldestTweetDateTime > datetimeLimit:
                while True:
                    oldestId = filteredTweets[-1].id
                    tweetsBatch = self.api.user_timeline(screen_name=self.userId,
                                                         tweet_mode='extended',
                                                         count=TweetsPerRequestMax,
                                                         max_id=oldestId - 1
                                                         )
                    filteredTweets = self._filterTweetsYoungerThanDateTimeLimit(tweetsList=tweetsBatch,
                                                                                datetimeLimit=datetimeLimit)
                    if len(filteredTweets) > 0:
                        allTweets.extend(filteredTweets)
                        print(f"Still fetching tweets, got {len(allTweets)} tweets so far from Twitter API.")
                        print('The oldest fetched tweet (no filter) date: ', tweetsBatch[-1].created_at)
                        print('The oldest (filtered) tweet date: ', filteredTweets[-1].created_at)
                    else:
                        break
        else:
            print('There was no tweets to fetch.')

        return allTweets

    def _isTweetWorthSaving(self, tweetStatus):
        mentionedUsers = [(x['screen_name']).lower() for x in tweetStatus.entities['user_mentions']]

        # only tweets which are at least 24 hours old will have reliable reaction count
        # and we will have full stock data from integrations for them
        datetimeLimit = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)
        tweetCreatedAtTimezoneAware = tweetStatus.created_at.replace(tzinfo=datetime.timezone.utc)

        if (((self.companyOfInterest).lower() in mentionedUsers) or
           (re.search(rf"\b{self.companyOfInterest}\b", tweetStatus.full_text, re.IGNORECASE))) and \
           tweetCreatedAtTimezoneAware < datetimeLimit:
            return True
        else:
            return False

    def _writeToFileOnlyNeededTweets(self, listOfTweets):
        print('Saving tweets in database')
        howManySavedTweets = 0

        # we expect that listofTweets has the newest tweets in the begining of the list
        for tweet in reversed(listOfTweets):
            # If tweet contains needed data then save it to file
            if self._isTweetWorthSaving(tweet):
                htmlElem = self.getHtmlForTweet(tweet.id)
                Tweet.objects.create(externalId=tweet.id,
                                     date=tweet.created_at.replace(tzinfo=datetime.timezone.utc),
                                     text=tweet.full_text,
                                     retweets=tweet.retweet_count,
                                     favorites=tweet.favorite_count,
                                     tweetHtml=htmlElem
                                     )
                howManySavedTweets += 1

        print(f"Saved {howManySavedTweets} tweets that matched criteria.")

    def populateDbFromScratch(self):
        # Fetch tweets from TweeterApi
        allTweets = self._getAllTweetsThatArePossibleToFetch()

        self._writeToFileOnlyNeededTweets(allTweets)

    def updateDbToThisMoment(self):
        # 1. Grab the last tweet Id that is present in the database
        # objects.first() because we are sorting Tweets, to have the newest one on the top
        biggestIdInFile = Tweet.objects.first().externalId
        # 2. Check if there are any newer tweets in API than the last tweet in the db
        allTweets = []

        tweetsBatch = self.api.user_timeline(screen_name=self.userId,
                                             tweet_mode='extended',
                                             count=200,
                                             since_id=biggestIdInFile
                                             )
        if len(tweetsBatch) > 0:
            oldestId = tweetsBatch[-1].id
            allTweets.extend(tweetsBatch)

            # keep looping through tweets (from the newest tweet to the oldest,
            # till we found (actually get past) the last tweet that was present in the dataFile)
            while True:
                tweetsBatch = self.api.user_timeline(screen_name=self.userId,
                                                     tweet_mode='extended',
                                                     count=200,
                                                     since_id=biggestIdInFile,
                                                     max_id=oldestId - 1
                                                     )
                if len(tweetsBatch) > 0:
                    allTweets.extend(tweetsBatch)
                    oldestId = tweetsBatch[-1].id
                    print(f"Still fetching tweets, got {len(allTweets)} tweets so far from Twitter API.")
                else:
                    break

            # 3. Save results to db
            print(f"Fetched {len(allTweets)} tweets in total from Twitter API.")
            self._writeToFileOnlyNeededTweets(allTweets)
        else:
            print('There was no tweets to fetch.')

    def getHtmlForTweet(self, TweetId):
        url = 'https://api.twitter.com/1.1/statuses/oembed.json'    # needs no auth
        payload = {'id': str(TweetId), 'theme': 'dark', 'omit_script': '1'}
        r = requests.get(url, params=payload)

        htmlForTweet = r.json()['html'].strip()

        return htmlForTweet

    # needed only to migrate from data file that didnt have the HtmlElem before
    # normally, this element should be added when creating a data file

    def _AddHtmlFieldToDataFile(self):
        tempDataFileName = 'tempDataFile.csv'
        tempDataFileLocation = os.path.join(self.dataDirName, tempDataFileName)
        with open(self.dataFileLocation, 'r', encoding='utf-8') as dataFile:
            with open(tempDataFileLocation, 'w', encoding='utf-8') as NewTempDataFile:
                writer = csv.writer(NewTempDataFile, lineterminator='\n')
                reader = csv.reader(dataFile)

                all = []
                row = next(reader)
                row.append('HtmlElement')
                all.append(row)

                counter = 0
                for row in reader:
                    htmlElem = self.getHtmlForTweet(row[0])
                    row.append(htmlElem)
                    all.append(row)
                    if counter < 0:
                        break
                    counter += 1

                writer.writerows(all)

        os.remove(self.dataFileLocation)
        os.rename(tempDataFileLocation, self.dataFileLocation)

    def createOrUpdateDb(self):
        if Tweet.objects.exists():
            self.updateDbToThisMoment()
        else:
            self.populateDbFromScratch()


if __name__ == '__main__':
    fetcher = TweetsFetcher(username='elonmusk', companyOfInterest='Tesla')
    fetcher.createOrUpdateDb()
