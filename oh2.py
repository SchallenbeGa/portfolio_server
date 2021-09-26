from pycoingecko import CoinGeckoAPI
import plotly.graph_objects as go
import pandas as pd
import datetime

cg = CoinGeckoAPI()
data = cg.get_coin_ohlc_by_id(id='bitcoin', vs_currency='usd',days='7')

df = pd.DataFrame(data)
line_list=[]
with open('tst.csv', 'w') as this_csv_file:
	line_list.append('Date,Open,High,Low,Close,Volume,Adjusted,dn,mavg,up,direction')
	for y in data:
		datet = datetime.datetime.utcfromtimestamp(y[0] / 1e3)
		line=f'{datet},{y[1]},{y[2]},{y[3]},{y[4]}'
		line_list.append(line)
	for line in line_list:
		this_csv_file.write(line)
		this_csv_file.write('\n')

df = pd.read_csv('tst.csv')

fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])

fig.show()