import csv
import os
import html
import re

import tweepy
import requests

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

        self.dataFileName = self.userId + '_Tweets.csv'
        self.dataDirName = 'data'
        self.dataFileLocation = os.path.join(self.dataDirName, self.dataFileName)
        if not os.path.isdir(self.dataDirName):
            os.mkdir(self.dataDirName)

        self.api = self._authorizeMe()

    def _authorizeMe(self):
        auth = tweepy.OAuthHandler(self.customer_key, self.customer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        api = tweepy.API(auth)
        return api

    def _getAllTweetsThatArePossibleToFetch(self):
        allTweets = []
        TweetsPerRequestMax = 200  # max allowed
        tweetsBatch = self.api.user_timeline(screen_name=self.userId,
                                             tweet_mode='extended',
                                             count=TweetsPerRequestMax
                                             )
        allTweets.extend(tweetsBatch)
        oldestId = tweetsBatch[-1].id

        while True:
            tweetsBatch = self.api.user_timeline(screen_name=self.userId,
                                                 tweet_mode='extended',
                                                 count=TweetsPerRequestMax,
                                                 max_id=oldestId - 1
                                                 )
            if len(tweetsBatch) > 0:
                allTweets.extend(tweetsBatch)
                oldestId = tweetsBatch[-1].id
                print('Len of allTweets is: ', len(allTweets))
                print('Last date is: ', tweetsBatch[-1].created_at)
            else:
                break

        return allTweets

    def _isTweetWorthSaving(self, tweetStaus):
        mentionedUsers = [(x['screen_name']).lower() for x in tweetStaus.entities['user_mentions']]
        if ((self.companyOfInterest).lower() in mentionedUsers) or \
           (re.search(rf"\b{self.companyOfInterest}\b", tweetStaus.full_text, re.IGNORECASE)):
            return True
        else:
            return False

    def _writeToFileOnlyNeededTweets(self, listOfTweets, writeHeaders=False):
        with open(self.dataFileLocation, 'a', newline='', encoding='utf-8') as dataFile:
            writer = csv.writer(dataFile)
            if writeHeaders:
                headers = ['Id',
                           'Date',
                           'Text',
                           'Retweets',
                           'Favorites',
                           'Hashtags',
                           'IsReply',
                           'MentionedUsers',
                           'HtmlElement']
                writer.writerow(headers)
            # we expect that listofTweets has the newest tweets in the begining of the list
            for tweet in reversed(listOfTweets):
                # If tweet contains needed data then save it to file
                if self._isTweetWorthSaving(tweet):
                    isReply = 0
                    if tweet.in_reply_to_user_id is not None:
                        isReply = 1
                    mentionedUsers = [x['screen_name'] for x in tweet.entities['user_mentions']]
                    hashtags = [x['text'] for x in tweet.entities['hashtags']]
                    htmlElem = self.getHtmlForTweet(tweet.id)
                    cleanedFullText = html.unescape(tweet.full_text.encode('utf-8').decode('utf-8)'))
                    cleanedFullText = cleanedFullText.replace('\n', '\\n')
                    # is it safe to have html unescaped here?
                    # TODO: Is escaping \n with \\n in full_text acceptable? Looks hacky
                    writer.writerow([tweet.id,
                                    tweet.created_at,
                                    cleanedFullText,
                                    tweet.retweet_count,
                                    tweet.favorite_count,
                                    hashtags,
                                    isReply,
                                    mentionedUsers,
                                    htmlElem])

    def createDataFile(self):
        # Fetch tweets from TweeterApi
        allTweets = self._getAllTweetsThatArePossibleToFetch()

        self._writeToFileOnlyNeededTweets(allTweets, writeHeaders=True)

    def updateDataFileToThisMoment(self):
        # 1. Grab the last tweet Id that is present in the file
        # If it is too slow, rewrite this part so we dont need to load entire file in memory
        with open(self.dataFileLocation, 'r', encoding='utf-8') as dataFile:
            lines = dataFile.readlines()
        lastLine = lines[-1]
        biggestIdInFile = int((lastLine.split(','))[0])
        print(biggestIdInFile)
        # 2. Check if there are any newer tweets than the last tweet in file
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
                    print('Len of allTweets is: ', len(allTweets))
                    print('Last date is: ', tweetsBatch[-1].created_at)
                else:
                    break

            # 3. Save results to file
            # Write a function to save only needed tweets to file. SaveHeaders=false as a param
            self._writeToFileOnlyNeededTweets(allTweets)

    def getHtmlForTweet(self, TweetId):
        url = 'https://api.twitter.com/1.1/statuses/oembed.json'    # needs no auth
        payload = {'id': str(TweetId), 'theme': 'dark', 'omit_script': '1'}
        r = requests.get(url, params=payload)
        htmlForTweet = r.json()['html'].strip()
        # print('Response is: ', htmlForTweet)
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

    def createOrUpdateDataFile(self):
        if os.path.isfile(self.dataFileLocation):
            self.updateDataFileToThisMoment()
        else:
            self.createDataFile()


if __name__ == '__main__':
    fetcher = TweetsFetcher('elonmusk', 'Tesla')
    fetcher.createOrUpdateDataFile()

# Note: To render HTML Elem correctly, replace "" with "
