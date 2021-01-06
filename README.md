# EMIOTS203

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
