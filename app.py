import matplotlib
matplotlib.use('Agg')
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
money = "cardano"
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
def s1(data, short_window, long_window,joker,budget_l):
	
	sma0 = joker
	sma1 = short_window
	sma2 = long_window
	buy_price = []
	sell_price = []
	sma_signal = []
	last_signal = 0
	signal = -1
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


def s2(data, short_window, long_window,joker,budget_l):	
	print("s2")
	sma0 = joker
	sma1 = short_window
	sma2 = long_window

	buy_price = []
	sell_price = []
	sma_signal = []

	last_buy = []
	last_sell = []

	last_signal = 0
	max_signal = 2
	signal = max_signal
	slic=budget_l/2
	profit = budget_l
	trade = []
	dispo = 0

	for i in range(len(data)):
		if sma1[i] > sma2[i]:
			if signal>0:
				buy_price.append(data[i])
				last_buy.append(data[i])
				last_signal = data[i]
				#print("buy : ",data[i]," dispo : ",dispo+slic/data[i])
				sell_price.append(np.nan)
				dispo += slic/data[i]
				signal-=1
				# print(profit)
				sma_signal.append(signal)
			else:
				buy_price.append(np.nan)
				sell_price.append(np.nan)
				sma_signal.append(0)
		elif sma2[i] > sma1[i]:
			if signal < max_signal:
				buy_price.append(np.nan)
				if(last_signal>data[i]):
					sell_price.append(np.nan)
					sma_signal.append(0)
				else:
					sell_price.append(data[i])
					profit += (slic/min(last_buy))*data[i] - slic
					last_sell.append(data[i])
					signal+=1
					dispo -= slic/min(last_buy)
					trade.append(profit-budget_l)
					sma_signal.append(-1)
					la = last_buy.pop(-1)
					if(len(last_buy)==0):
						print("buy at : ",last_signal," sell at : ",data[i]," for (",slic/la,") :",(slic/la)*data[i]," profit : ",profit-budget_l)
					else:
						print("buy at : ",min(last_buy)," sell at : ",data[i]," for (",slic/la,") :",(slic/la)*data[i]," profit : ",profit-budget_l)
			else:
				buy_price.append(np.nan)
				sell_price.append(np.nan)
				sma_signal.append(0)
		else:
			buy_price.append(np.nan)
			sell_price.append(np.nan)
			sma_signal.append(0)
	
	return buy_price, sell_price, sma_signal,trade,(profit-budget_l)

@app.route("/<version>/<name>")
def currency(version,name):
	save(req(name,30))
	data = pd.read_csv('tst.csv').set_index('Date')
	data.index = pd.to_datetime(data.index)

	n = [10,20,50]
	for i in n:
		data[f'sma_{i}'] = sma(data['Close'], i)

	sma_10 = data['sma_10']
	sma_20 = data['sma_20']
	sma_50 = data['sma_50']

	if(version=="1"):
		print("good")
		buy_price, sell_price, signal,trade,profit =s1(data['Close'], sma_20, sma_10, sma_50,budget_l)
	else:
		buy_price, sell_price, signal,trade,profit =s2(data['Close'], sma_20, sma_10, sma_50,budget_l)

	f = plt.figure()
	f.set_figwidth(15)
	f.set_figheight(7)
	# print(version)
	# print(buy_price,sell_price)
	plt.plot(data['Close'], alpha = 0.3, label = 'data')
	plt.plot(sma_10, alpha = 0.6, label = 'SMA 10')
	plt.plot(sma_20, alpha = 0.6, label = 'SMA 20')
	plt.plot(sma_50, alpha = 0.6, label = 'SMA 50')
	plt.scatter(data.index, buy_price, marker = '^', s = 200, color = 'darkblue', label = 'BUY SIGNAL')
	plt.scatter(data.index, sell_price, marker = 'v', s = 200, color = 'crimson', label = 'SELL SIGNAL')
	plt.legend(loc = 'upper left')
	if(len(trade)!=0):
		title = 'SMA 10-20 reverse cross '+version+' \n currency : '+name+' budget : '+str(budget_l)+'\n profit :'+str(profit)+'\n avg profit : '+str(sum(trade)/len(trade))
	else: title = 'SMA 10-20 reverse cross '+version+' \n currency : '+name+' budget : '+str(budget_l)+'\n profit : niet nada'
	plt.title(title)
	buf = BytesIO()
	plt.savefig(buf, format="png")
	# Embed the result in the html output.
	dat = base64.b64encode(buf.getbuffer()).decode("ascii")
	return f"<img src='data:image/png;base64,{dat}'/>"
