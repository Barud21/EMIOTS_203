# EMIOTS203

It is a web application (using Django) that allows you to check if tweets posted by elonmusk account and containing a reference to Tesla had any influence on TSLA results on NYSE.

The name is an acronym for Elon Musk Influence On Tesla Stock. 203 part doesn't have any meaning :)

## How it works?

It consists of 3 main parts:

- TweetsFetcher - is a script that uses `tweepy` library to get tweets from Twitter Api
- StockData - is a script that uses `yfinance` library to fetch stock market data and generates graphs representing this data
- Django application - allows to visualize both tweets and stock graphs

To periodically poll for the new data we are using `celery` library along with `django-celery-beat` for a cool management panel in django-admin.

Data polling task is configured to run once a day. The following acions are executed during this task:

- get tweets from Twitter API that are newer than last saved tweet
- check if any of these tweets is relevant (by mentioning Tesla account or just having a word Tesla inside), if yes then save it to database
- get stock data for 3 hours before and after tweet's date
- generate a graph with fetched stock data and save it into database

## Example data

To make your life easier when testing this project, we provided example data sets that you can import to your database. This way, you can get the feel of this project by yourself while waiting for approval of your Twitter developper account.

Example data is present in the `data` directory. It consists of 2 files:  

- elonmusk_Tweets.csv - containng prefetched tweets from elonmusk account, that are somehow related to Tesla
- stock_data.csv - containing stock data from a timerange that allows to generate a graphs for tweets example dataset

### How to migrate

1. Migrate tweets and stock charts

    - Run `python .\manage.py shell`
    - In the shell, execute the following

        ```python
        exec(open('dataMigration.py').read())
        ```

    This process assumes that you have an empty Tweet and StockChart tables. This command migrates tweets and stockcharts to tables, it will print how many tweets were imported to database or info that Tweet or StockChart table consists some data and migration did not take place.

## Waking up free heroku dynos

We have been using free heroku dynos for our deployments. Those dynos go to sleep if web dyno hasn't received any web traffic for some time. For data updates we use celery periodic tasks. However, when dyno is in sleep mode, then it will not trigger the task and data will not be updated.

A workaround for this problem we eventually used is to use an external service that will make a HTTP request to our web dyno, which will wake all other dynos. We've chosen <https://www.statuscake.com> which allows to easily set up a GET request monitor, which will wake up our dynos in 24h intervals. In this way, when celery periodic task is scheduled to run at 10am, we set a monitor through statuscake to run everyday at 9:50am. It will ensure our dyno will be up and runnig at 10am and periodic task will be executed.
