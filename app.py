import math
import datetime
import time
import os
import json

import pandas as pd
from flask import Flask
from flask import render_template,redirect

from pycoingecko import CoinGeckoAPI

app = Flask(__name__)

cg = CoinGeckoAPI()

currencies = pd.read_csv('budget-example.csv')

def save(name,days,pat):
	data = cg.get_coin_ohlc_by_id(id=name, vs_currency='usd',days=days)
	line_list=[]
	with open(pat, 'w') as this_csv_file:
		line_list.append('Date,Open,High,Low,Close,Volume')
		for y in data:
			datet = datetime.datetime.fromtimestamp(y[0] / 1e3)
			line=f'{datet},{y[1]},{y[2]},{y[3]},{y[4]}'
			line_list.append(line)
		for line in line_list:
			this_csv_file.write(line)
			this_csv_file.write('\n')

@app.route("/refresh")
def refresh():
	for n in 1,30:
		for i,z,buy in currencies.values:
			pat = 'data/'+i+'_'+str(n)+'.csv'
			if(os.path.exists(pat)):
				if (int(time.time()) - 60 * 5) > int((os.path.getmtime(pat))):
					print("download ",n,": ",i)
					save(i,n,pat)
			else:
				print("download ",n,": ",i)
				save(i,n,pat)
	return redirect('/')

@app.route("/edit")
def edit():
	trade = []

	for i,z,buy in currencies.values:
		tr = {"money":i,"quantity":z,"buy_price":buy}
		trade.append(tr)

	return render_template("edit.html",trade=trade)

@app.route("/")
def home():

	for n in 1,30:
		for i,z,buy in currencies.values:
			pat = 'data/'+i+'_'+str(n)+'.csv'
			if(os.path.exists(pat)):
				if (int(time.time()) - 60 * 5) > int((os.path.getmtime(pat))):
					print("download ",n,": ",i)
					save(i,n,pat)
			else:
				print("download ",n,": ",i)
				save(i,n,pat)

	trade = []

	for i,z,buy in currencies.values:
		data = pd.read_csv('data/'+i+'_30.csv')
		data.index = pd.to_datetime(data.index)	

		data_p = pd.read_csv('data/'+i+'_1.csv')
		data_p.index = pd.to_datetime(data_p.index)	
		
		sma_10 = pd.DataFrame(data['Close'].rolling(window=10).mean()).max()['Close']
		sma_20 = pd.DataFrame(data['Close'].rolling(window=20).mean()).max()['Close']
		sma_30 = pd.DataFrame(data['Close'].rolling(window=30).mean()).max()['Close']
		comment = "nada"
	
		if (data_p['Close'].iloc[-1]>sma_10) :
			comment = "hold"
			if (data_p['Close'].iloc[-1]>sma_10) & (data_p['Close'].iloc[-1]>sma_20)  :
				comment = "may sell"
				if (data_p['Close'].iloc[-1]>sma_10) & (data_p['Close'].iloc[-1]>sma_20) & (data_p['Close'].iloc[-1]>sma_30)  :
					comment = "SELL !!!"

		if (data_p['Close'].iloc[-1]<sma_10)  :
			comment = "risky buy"
			if (data_p['Close'].iloc[-1]<sma_10) & (data_p['Close'].iloc[-1]<sma_20)  :
				comment = "may buy"
				if (data_p['Close'].iloc[-1]<sma_10) & (data_p['Close'].iloc[-1]<sma_20) & (data_p['Close'].iloc[-1]<sma_30)  :
					comment = "BUY !!!"
	
		# print("money : ",i," price : ",data_p['Close'].iloc[-1],"sma 10 : ",sma_10,"sma 20 : ",sma_20,"sma 30 : ",sma_30," advice : ",comment)
		tr = {"money":i,"quantity":z,"price":data_p['Close'].iloc[-1],"buy_price":buy,"sma_10":sma_10,"sma_20":sma_20,"sma_30":sma_30,"comment":comment}
		trade.append(tr)

	return render_template("index.html",trade=trade)

@app.route("/api")
def api():
	trade = []
	for i,z,buy in currencies.values:
		tr = {"money":i,"quantity":z,"buy_price":buy}
		trade.append(tr)

	return json.dumps(trade)