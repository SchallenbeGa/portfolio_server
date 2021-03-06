import math
import datetime
import time
import os
import json

import pandas as pd
from flask import Flask
from flask import render_template,redirect,request
from flask_cors import CORS
from pycoingecko import CoinGeckoAPI

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

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

def save_budget(data):
	line_list=[]
	with open("budget-example.csv", 'w') as this_csv_file:
		line_list.append('name,hold,buy_price')
		for y in data:
			print(y["money"])
			line= str(y["money"])+","+str(y["quantity"])+","+str(y["buy_price"])
			line_list.append(line)
		for line in line_list:
			this_csv_file.write(line)
			this_csv_file.write('\n')

@app.route("/edit")
def edit():
	currencies = pd.read_csv('budget-example.csv')
	trade = []
	for i,z,buy in currencies.values:
		tr = {"money":i,"quantity":z,"buy_price":buy}
		trade.append(tr)

	return render_template("edit.html",trade=trade)

@app.route('/edit',methods = ['POST'])
def save_d():

	money = request.form["money"].lower()
	buy_price = request.form['buy_price']
	quantity = request.form['quantity']

	trade = []
	for i,z,buy in currencies.values:
		if(i==money):
			i = money
			z = quantity
			buy = buy_price
		trade.append({"money":i,"quantity":z,"buy_price":buy})
	save_budget(trade)

	return redirect('edit')

@app.route('/trash',methods = ['POST'])
def trash():
	
	money = request.form["money"].lower()

	trade = []
	for i,z,buy in currencies.values:
		if(i!=money):
			trade.append({"money":i,"quantity":z,"buy_price":buy})
	save_budget(trade)	

	return redirect('edit')

@app.route('/new',methods = ['POST'])
def new():
	
	money = request.form["money"].lower()
	buy_price = request.form['buy_price']
	quantity = request.form['quantity']

	trade = []
	for i,z,buy in currencies.values:
		trade.append({"money":i,"quantity":z,"buy_price":buy})
	trade.append({"money":money,"quantity":quantity,"buy_price":buy_price})
	save_budget(trade)	

	return redirect('edit')

@app.route("/")
def home():
	currencies = pd.read_csv('budget-example.csv')
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
		
		pnl = (z*data_p['Close'].iloc[-1])-(z*buy)
		
		tr = {"pnl":pnl,"money":i,"quantity":z,"price":data_p['Close'].iloc[-1],"buy_price":buy,"sma_10":sma_10,"sma_20":sma_20,"sma_30":sma_30,"comment":comment}
		trade.append(tr)

	return render_template("index.html",trade=trade)

@app.route("/api")
def api():
	currencies = pd.read_csv('budget-example.csv')
	for n in 1,30:
		for i,z,buy in currencies.values:
			pat = 'data/'+i+'_'+str(n)+'.csv'
			if(os.path.exists(pat)):
				if (int(time.time()) - 60 * 60) > int((os.path.getmtime(pat))):
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
		
		pnl = (z*data_p['Close'].iloc[-1])-(z*buy)
		
		tr = {"pnl":pnl,"money":i,"quantity":z,"price":data_p['Close'].iloc[-1],"buy_price":buy,"sma_10":sma_10,"sma_20":sma_20,"sma_30":sma_30,"comment":comment}
		trade.append(tr)

	return json.dumps(trade)