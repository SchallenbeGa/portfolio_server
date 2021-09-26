from pycoingecko import CoinGeckoAPI
import pandas as pd

def read_API(req,c,num_rows):
    coin = pd.DataFrame.from_records(req)
    coin = coin[[c]]
    #coin = coin.sort_values(by=c, ascending=False)
    coins = coin.head(num_rows)

    print(coins)
    return coins

#store data to CSV format
def store_data(data_frame):
    data_frame.to_csv("crypto_top.csv", index=False)

cg = CoinGeckoAPI()

last = cg.get_price(ids='monero,ripple', vs_currencies='usd', include_market_cap=True)
print(last)
tr = read_API(last,'ripple',10)
store_data(tr)
	   