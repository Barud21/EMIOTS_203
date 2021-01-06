from EMIOTS203.tweetsFetcher import TweetsFetcher
from EMIOTS203.stockData import StockData

# Tweets migration
fetcher = TweetsFetcher(username='elonmusk', companyOfInterest='Tesla')
print("Tweets migration:")
fetcher.migrateDataFromCsvToDatabase()
print("")

# Stockchart migration
stockData = StockData()
print("Stock charts migration:")
stockData.migrateStockFromCsvToDatabase()
