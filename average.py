from pycoingecko import CoinGeckoAPI
import plotly.graph_objects as go
import pandas as pd
import datetime

cg = CoinGeckoAPI()
days = "1"
money = "ripple"
data = cg.get_coin_ohlc_by_id(id=money, vs_currency='usd',days=days)

df = pd.DataFrame(data)
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

df = pd.read_csv('tst.csv')
low_av = df["Low"].mean()
high_av = df["High"].mean()
low = df.min()['Low']
high = df.max()['High']
diff_av = (high_av - low_av) / (low_av/100)
diff = (high - low) / (low/100)

print("Currency : ",money)
print("Days : ",days)
print("--------------------------------")
print("Low average : ",low_av)
print("High average : ",high_av)
print("Difference average : ",diff_av,"%")
print("--------------------------------")
print("Lowest : ",low)
print("Highest : ",high)
print("Difference : ",diff,"%")
print("--------------------------------")
print("Actual : ",df.at[df.last_valid_index(),'Close'])
print("--------------------------------")