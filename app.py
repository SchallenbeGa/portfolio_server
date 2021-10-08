import matplotlib
matplotlib.use('Agg')

import datetime
import base64
from io import BytesIO

import pandas as pd
import numpy as np

import mplfinance as mpf
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from pycoingecko import CoinGeckoAPI
from flask import Flask
from flask import render_template,redirect
app = Flask(__name__)

cg = CoinGeckoAPI()

days = "1"
money = "cardano"
budget_l = 1000

def req(money,days):

	data = cg.get_coin_ohlc_by_id(id=money, vs_currency='usd',days=days)
	d1 = {'Date':[],'Open':[],'High':[],'Low':[],'Close':[]}

	for y in data:
		d1['Date'].append(datetime.datetime.fromtimestamp(y[0] / 1e3))
		d1['Open'].append(y[1])
		d1['High'].append(y[2])
		d1['Low'].append(y[3])
		d1['Close'].append(y[4])

	return pd.DataFrame(d1).set_index('Date')

def sma(data, n):
	sma = data.rolling(window=n).mean()
	return pd.DataFrame(sma)

def s1(data, short_window, long_window,budget_l):

	buy_price = []
	sell_price = []
	sma_signal = []

	last_buy = []
	last_sell = []

	trade = []
	trade_r = []

	sma1 = short_window
	sma2 = long_window

	dispo = 0
	last_signal = 0
	signal = 1
	slic=budget_l/1
	profit = budget_l

	for i in range(len(data)):
		if sma1[i] > sma2[i]:
			if signal>0:
				buy_price.append(data[i])
				last_buy.append(data[i])
				last_signal = data[i]
				sell_price.append(float('nan'))
				dispo += slic/data[i]
				signal-=1
				sma_signal.append(signal)
			else:
				buy_price.append(float('nan'))
				sell_price.append(float('nan'))
				sma_signal.append(0)
		elif sma2[i] > sma1[i]:
			if signal < 1:
				buy_price.append(float('nan'))
				if(max(last_buy)>data[i]):
					sell_price.append(float('nan'))
					sma_signal.append(0)
				else:
					sell_price.append(data[i])
					tr = {"buy_price":min(last_buy)}
					profit += (slic/min(last_buy))*data[i] - slic
					last_sell.append(data[i])
					signal+=1
					dispo -= slic/min(last_buy)
					sma_signal.append(-1)
					la = last_buy.pop(-1)
					trade.append(((slic/la)*data[i])-slic)
					tr["quantity"] = slic/la
					tr["sell_price"] = data[i]
					tr["profit"] = ((slic/la)*data[i])-slic
					tr["budget"] = profit
					trade_r.append(tr)
					slic=(slic/la)*data[i]		
			else:
				buy_price.append(float('nan'))
				sell_price.append(float('nan'))
				sma_signal.append(0)
		else:
			buy_price.append(float('nan'))
			sell_price.append(float('nan'))
			sma_signal.append(0)
	
	return buy_price, sell_price, sma_signal,trade,trade_r,(profit-budget_l)

@app.route('/')
def home():
	return redirect('/monero/30/8000')

@app.route("/<name>/<days>/<budget_l>")
def currency(name,days,budget_l):

	data = req(name,days)
	data.index = pd.to_datetime(data.index)

	#print(data.value_counts())
	
	# df1 = pd.DataFrame(data=data['Open'].value_counts(), columns=[['Open','Count']])
	# df1['Count']=df1['Open'].index
	
	# print(list(df1[df1['Open']==df1.Number.max()]['Count']))

	n = [10,20,50]
	for i in n:
		data[f'sma_{i}'] = sma(data['Close'], i)

	sma_10 = data['sma_10']
	sma_20 = data['sma_20']
	sma_50 = data['sma_50']

	buy_price, sell_price, signal,trade,trade_r,profit = s1(data['Close'],sma_20, sma_10,int(budget_l))

	buf = BytesIO()
	mpf.plot(data,
			type='candle',
			figscale=2.2,
			fill_between=dict(y1=data['Low'].mean(),y2=data['High'].mean()),
			datetime_format=' %A, %d-%m-%Y',
			xrotation=45,
			style='charles',
            ylabel='Price ($)',
            ylabel_lower='Shares \nTraded', 
            mav=(3,6,9),
			savefig=buf)

	plt.close()
	f = plt.figure()
	f.set_figwidth(15)
	f.set_figheight(7)

	plt.plot(data['Close'], alpha = 0.3, label = 'data')
	plt.plot(sma_10, alpha = 0.6, label = 'SMA 10')
	plt.plot(sma_20, alpha = 0.6, label = 'SMA 20')
	plt.plot(sma_50, alpha = 0.6, label = 'SMA 50')

	plt.legend(loc = 'upper left')

	title = 'nada niet'

	if(len(trade)!=0):
		plt.scatter(data.index, buy_price, marker = '^', s = 200, color = 'darkblue', label = 'B')
		plt.scatter(data.index, sell_price, marker = 'v', s = 200, color = 'crimson', label = 'S')
		title = 'trade : ' + str(profit/(sum(trade)/len(trade))) + ' avg profit : '+str(sum(trade)/len(trade))
	dat = base64.b64encode(buf.getbuffer()).decode("ascii")
	return render_template("base.html",profit=profit,title = title,trade_l=len(trade_r),trade = trade_r,dat = dat,currency = name,budget=budget_l)

if __name__ == '__main__':
   app.run(debug = True)
