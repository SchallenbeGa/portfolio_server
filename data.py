import datetime
import pandas as pd
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

days = "1"
money = "ripple"

def req(money="ripple",days=1):
	data = cg.get_coin_ohlc_by_id(id=money, vs_currency='usd',days=days)
	return data

def save(data):
	line_list=[]
	with open('tst.csv', 'w') as this_csv_file:
		line_list.append('Date,Open,High,Low,Close,Volume')
		for y in data:
			datet = datetime.datetime.fromtimestamp(y[0] / 1e3)
			line=f'{datet},{y[1]},{y[2]},{y[3]},{y[4]}'
			line_list.append(line)
		for line in line_list:
			this_csv_file.write(line)
			this_csv_file.write('\n')
save(req("bitcoin",30))