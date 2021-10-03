import matplotlib
matplotlib.use('Agg')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import datetime
from pycoingecko import CoinGeckoAPI
from flask import Flask,render_template,redirect
from matplotlib.figure import Figure

app = Flask(__name__)


cg = CoinGeckoAPI()

days = "1"
money = "cardano"
budget_l = 1000

#get money info from coingecko
def req(money,days):
	data = cg.get_coin_ohlc_by_id(id=money, vs_currency='usd',days=days)
	return data

# def r_get_coin_list():
# 	data = cg.get_coins_list()
# 	#print(data)
# 	save_coins(data)
# 	data = get_coin_list()
# 	return data

# def save_coins(data):
# 	line_list=[]
# 	with open('coins.csv', 'w',encoding="utf-8") as this_csv_file:
# 		line_list.append('id,symbol,name,n,y,z')
# 		for y in data:
# 			line=f'{y["id"]},{y["symbol"]},{y["name"]}'
# 			line_list.append(line)
# 		for line in line_list:
# 			print(line)
# 			this_csv_file.write(line)
# 			this_csv_file.write('\n')

def get_coin_list():
	return pd.read_csv('coins.csv')
#format & save data as tst.csv
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

#get simple moving average 10,20,and 30-50 day
def sma(data, n):
	sma = data.rolling(window=n).mean()
	return pd.DataFrame(sma)

#strategy
def s2(data, short_window, long_window,budget_l,nb_trade,ad):	

	sma1 = short_window
	sma2 = long_window

	buy_price = []
	sell_price = []
	sma_signal = []

	last_buy = []
	last_sell = []

	last_signal = 0
	signal = nb_trade
	slic=budget_l/nb_trade
	profit = budget_l
	trade = []
	trade_r = []
	dispo = 0

	for i in range(len(data)):
		if sma1[i] > sma2[i]:
			if signal>0:
				buy_price.append(data[i])
				last_buy.append(data[i])
				last_signal = data[i]
				sell_price.append(np.nan)
				dispo += slic/data[i]
				signal-=1
				sma_signal.append(signal)
			else:
				buy_price.append(np.nan)
				sell_price.append(np.nan)
				sma_signal.append(0)
		elif sma2[i] > sma1[i]:
			if signal < nb_trade:
				buy_price.append(np.nan)
				if(max(last_buy)>data[i]):
					sell_price.append(np.nan)
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
					if(ad==1):
						slic=(slic/la)*data[i]
					
			else:
				buy_price.append(np.nan)
				sell_price.append(np.nan)
				sma_signal.append(0)
		else:
			buy_price.append(np.nan)
			sell_price.append(np.nan)
			sma_signal.append(0)
	
	return buy_price, sell_price, sma_signal,trade,trade_r,(profit-budget_l)


def brutus(data, short_window, long_window,budget_l,nb_trade,ad):	

	sma1 = short_window
	sma2 = long_window

	buy_price = []
	sell_price = []
	sma_signal = []

	last_buy = []
	last_sell = []

	last_signal = 0
	signal = nb_trade
	slic=budget_l/nb_trade
	profit = budget_l
	trade = []
	trade_r = []
	dispo = 0

	for i in range(len(data)):

		if (signal < nb_trade) & (dispo>0):
			if(max(last_buy)<data[i]):
				sell_price.append(data[i])
				buy_price.append(np.nan)
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
				if(ad==1):
					slic=(slic/la)*data[i]
			else:
				buy_price.append(np.nan)
				sell_price.append(np.nan)
				sma_signal.append(0)

		elif sma1[i] < sma2[i]:
			if signal>0:
				("buy at : ",data[i])
				buy_price.append(data[i])
				last_buy.append(data[i])
				last_signal = data[i]
				sell_price.append(np.nan)
				dispo += slic/data[i]
				signal-=1
				sma_signal.append(signal)
			else:
				buy_price.append(np.nan)
				sell_price.append(np.nan)
				sma_signal.append(0)
		else:
			buy_price.append(np.nan)
			sell_price.append(np.nan)
			sma_signal.append(0)

	return buy_price, sell_price, sma_signal,trade,trade_r,(profit-budget_l)


@app.route('/')
def home():
	return redirect('/1/1/monero/30')

@app.route("/<sr>/<version>/<name>/<days>")
def currency(sr,version,name,days):

	save(req(name,days))
	data = pd.read_csv('tst.csv').set_index('Date')
	data.index = pd.to_datetime(data.index)

	n = [10,20,50]
	for i in n:
		data[f'sma_{i}'] = sma(data['Close'], i)

	sma_10 = data['sma_10']
	sma_20 = data['sma_20']
	sma_50 = data['sma_50']

	switch={
      "1":[1,0],
      "2":[2,0],
	  "3":[2,1]
    }
	version = switch.get(version,"Invalid input")
	if(sr=="1"):
		buy_price, sell_price, signal,trade,trade_r,profit = s2(data['Close'],sma_20, sma_10,budget_l,version[0],version[1])
	elif sr == "2":
		buy_price, sell_price, signal,trade,trade_r,profit = s2(data['Close'],sma_10, sma_20,budget_l,version[0],version[1])
	elif sr == "3":
		buy_price, sell_price, signal,trade,trade_r,profit = brutus(data['Close'],sma_20, sma_10,budget_l,version[0],version[1])
	elif sr == "4":
		buy_price, sell_price, signal,trade,trade_r,profit = brutus(data['Close'],sma_10, sma_20,budget_l,version[0],version[1])
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

	buf = BytesIO()
	plt.savefig(buf, format="png")
	dat = base64.b64encode(buf.getbuffer()).decode("ascii")
	coins = get_coin_list()
	return render_template("base.html",profit=profit,title = title,trade_l=len(trade_r),trade = trade_r,dat = dat,currency = name,coins=coins,coins_len=len(coins),sr=sr)

if __name__ == '__main__':
   app.run(debug = True)
