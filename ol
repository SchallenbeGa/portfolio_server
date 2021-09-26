import pandas as pd
from pycoingecko import CoinGeckoAPI

#Getting data from coingecko API
cg = CoinGeckoAPI()
report = cg.get_coins_markets(vs_currency= "usd")
print(type(report))

#Reading json file from API using pandas
#Sorting values in descending order based on Market cap.
def read_API(req= report,num_rows=10):
    coin_df = pd.DataFrame.from_records(req)
    coin_df = coin_df[["name", "current_price", "market_cap"]]
    coin_df = coin_df.sort_values(by="market_cap", ascending=False)
    coins = coin_df.head(num_rows)
    #Renaming columns in Data Frame 
    coins = coins.rename(columns = {'name': 'Coin', 'current_price': 'Price', 'market_cap': 'Market Capitalization'}, inplace = False)
    #Printing sorted values for review
    print(coins)
    return coins

#store data to CSV format
def store_data(data_frame):
    data_frame.to_csv("crypto_top.csv", index=False)


read_API(report,10)