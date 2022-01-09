import pandas as pd
import numpy as np
import mplfinance as mpf
import base64
import config
from io import BytesIO
import datetime
from flask import Flask,render_template


app = Flask(__name__)

@app.route('/')
def home():
	data = pd.read_csv('tst.csv').set_index('Date')
	data.index = pd.to_datetime(data.index,format="%Y-%m-%d %H:%M:%S")

	trade = pd.read_csv('trade.csv')
	trade_d = trade
	trade.set_index('Date')

	buf = BytesIO()
	fees = []	
	gains = []
	s  = mpf.make_mpf_style(base_mpf_style="yahoo",facecolor="#282828",gridcolor="#212121",rc={'xtick.color':'#f8f8f8','ytick.color':'#f8f8f8','axes.labelcolor':'#f8f8f8'})
		
	if len(trade)>0 :
		
		buy = []
		sell = []
		trade_f = []
		for x in range(len(trade)):
			if len(trade)>1:
				if(x<=len(trade)-2):
					print(trade['Price'][x])
					gains.append(trade['Price'][x+1]*int(config.QUANTITY)-trade['Price'][x]*int(config.QUANTITY))
			fees.append(((trade['Price'][x]*int(config.QUANTITY))/100)*0.1)
			trade_f.append(datetime.datetime.strptime(trade_d['Date'][x],"%Y-%m-%d %H:%M:%S").minute)

		for i in range(len(data)):
			is_done = False
			if data.index.array[i].minute in trade_f:
				print("maybe")
				for x in range(len(trade)):
					if((data.index.array[i].minute==datetime.datetime.strptime(trade_d['Date'][x],"%Y-%m-%d %H:%M:%S").minute) & (data.index.array[i].hour==datetime.datetime.strptime(trade_d['Date'][x],"%Y-%m-%d %H:%M:%S").hour)):
						print("start")
						is_done = True
						print(data['Low'][i])
						print(trade['Price'][x])	
						if(trade['Type'][x]=="buy"):
							buy.append(trade['Price'][x]-0.003)
						else:
							sell.append(trade['Price'][x]+0.003)
			if not is_done:
				buy.append(np.nan)
				sell.append(np.nan)
		if len(trade)>1:
			if len(trade)%2 != 0:
				sell.append(np.nan)

		for x in range(int((len(trade)-2)/2)):
			buy.append(np.nan)
			sell.append(np.nan)

		print(buy)
		print(len(data))
		print(len(buy))
		print(len(sell))

		if len(data)>len(buy):
			buy.append(np.nan)
			sell.append(np.nan)
		
		sell_n = 0
		for v in sell :              
			if not np.isnan(v):     
				sell_n+=1

		if sell_n>0:
			apd = [
				mpf.make_addplot(buy, scatter=True, markersize=200, marker=r'^', color='green'),
				mpf.make_addplot(sell, scatter=True, markersize=200, marker=r'v', color='red')
			]
		else:
			apd = [mpf.make_addplot(buy, scatter=True, markersize=200, marker=r'^', color='green')]
			print("py")
		fig,ax = mpf.plot(
			data,
			addplot=apd,
			type='candle',
			volume=True,
			style=s,
			mav=(8),
			figscale=1,
			figratio=(20,10),
			datetime_format="%d %H:%M:%S",
			xrotation=0,
			returnfig=True)
		fig.savefig(buf,facecolor='#282828')
	else:
		fig,ax = mpf.plot(
			data,
			type='candle',
			volume=True,
			style=s,
			mav=(8),
			figratio=(20,10),
			datetime_format="%d %H:%M:%S",
			xrotation=0,
			returnfig=True)
		fig.savefig(buf,facecolor='#282828')

	order = pd.read_csv('order.csv')
	dat = base64.b64encode(buf.getbuffer()).decode("ascii")
	print(fees)
	return render_template("base.html",dat = dat,trade=trade_d,trade_l=len(trade_d),order=order,order_l=len(order),pair=config.PAIR_M,last_price=data['Close'][-1],fee=fees,fee_l=len(fees),gain=gains,gain_l=len(gains))

if __name__ == '__main__':
   app.run(debug = True)