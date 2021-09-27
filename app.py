import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import datetime
from pycoingecko import CoinGeckoAPI
from flask import Flask
from matplotlib.figure import Figure

app = Flask(__name__)


cg = CoinGeckoAPI()

days = "1"
money = "qtum"
budget_l = 1000

def req(money,days):
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


def sma(data, n):
	sma = data.rolling(window=n).mean()
	return pd.DataFrame(sma)

def implement_sma_strategy(data, short_window, long_window,joker,budget_l):

	sma0 = joker
	sma1 = short_window
	sma2 = long_window
	buy_price = []
	sell_price = []
	sma_signal = []
	last_signal = 0
	signal = 0
	profit = budget_l
	trade = []
	dispo = 0

	for i in range(len(data)):
		if sma1[i] > sma2[i]:
			if signal != 1: #
				buy_price.append(data[i])
				last_signal = data[i]
				print("buy : ",data[i])
				sell_price.append(np.nan)
				signal = 1
				dispo = profit/data[i]
				profit =profit-budget_l
				print(profit)
				sma_signal.append(signal)
			else:
				buy_price.append(np.nan)
				sell_price.append(np.nan)
				sma_signal.append(0)
		elif sma2[i] > sma1[i]:
			if signal != -1:
				buy_price.append(np.nan)
				if(last_signal>data[i]):
					sell_price.append(np.nan)
					sma_signal.append(0)
				else:
					sell_price.append(data[i])
					print("sell : ",data[i])
					profit = dispo*data[i]
					print(profit)
					dispo = 0
					trade.append(profit-budget_l)
					signal = -1
					sma_signal.append(-1)
			else:
				buy_price.append(np.nan)
				sell_price.append(np.nan)
				sma_signal.append(0)
		else:
			buy_price.append(np.nan)
			sell_price.append(np.nan)
			sma_signal.append(0)
		
	return buy_price, sell_price, sma_signal,trade,(profit)

save(req(money,30))

data = pd.read_csv('tst.csv').set_index('Date')
data.index = pd.to_datetime(data.index)

n = [10,20,50]
for i in n:
	data[f'sma_{i}'] = sma(data['Close'], i)

@app.route("/")
def hello():

	sma_10 = data['sma_10']
	sma_20 = data['sma_20']
	sma_50 = data['sma_50']

	buy_price, sell_price, signal,trade,profit = implement_sma_strategy(data['Close'], sma_20, sma_10, sma_50,budget_l)

	print(trade)

	f = plt.figure()
	f.set_figwidth(15)
	f.set_figheight(7)

	plt.plot(data['Close'], alpha = 0.3, label = 'data')
	plt.plot(sma_10, alpha = 0.6, label = 'SMA 10')
	plt.plot(sma_20, alpha = 0.6, label = 'SMA 20')
	plt.plot(sma_50, alpha = 0.6, label = 'SMA 50')
	plt.scatter(data.index, buy_price, marker = '^', s = 200, color = 'darkblue', label = 'BUY SIGNAL')
	plt.scatter(data.index, sell_price, marker = 'v', s = 200, color = 'crimson', label = 'SELL SIGNAL')
	plt.legend(loc = 'upper left')
	plt.title('SMA 10-20 reverse cross \n currency : '+money+' & budget : '+str(budget_l) +'\n profit :'+str(sum(trade))+'\n avg profit : '+str(sum(trade)/len(trade)))
	buf = BytesIO()
	plt.savefig(buf, format="png")
	# Embed the result in the html output.
	dat = base64.b64encode(buf.getbuffer()).decode("ascii")
	return f"<img src='data:image/png;base64,{dat}'/>"
