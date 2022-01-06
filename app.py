import pandas as pd
import numpy as np
import mplfinance as mpf
import base64
from io import BytesIO
import datetime
from flask import Flask,render_template,redirect


app = Flask(__name__)

@app.route('/')
def home():
	data = pd.read_csv('tst.csv').set_index('Date')
	data.index = pd.to_datetime(data.index)

	trade = pd.read_csv('trade.csv')

	buf = BytesIO()
	mpf.plot(data,type='candle',style="charles",volume=True,mav=(3,6,9),figscale=1.25,datetime_format='%I:%M:%S %p',xrotation=0,savefig=buf)
	print(trade['Date'].get(0))
	dat = base64.b64encode(buf.getbuffer()).decode("ascii")
	return render_template("base.html",dat = dat,trade=trade,trade_l=len(trade))

if __name__ == '__main__':
   app.run(debug = True)