import matplotlib
matplotlib.use('Agg')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import datetime
from flask import Flask,render_template,redirect


app = Flask(__name__)

@app.route('/')
def home():
	data = pd.read_csv('tst.csv').set_index('Date')
	data.index = pd.to_datetime(data.index)

	trade = pd.read_csv('trade.csv').set_index('Date')
	trade.index = pd.to_datetime(trade.index)

	plt.close()
		 
  
	plt.figure()
	

	up = data[data.Close >= data.Open]

	down = data[data.Close < data.Open]

	col1 = 'red'

	col2 = 'green'
	
	width = 0.1
	width2 = 0.1
	
	# Plotting up prices of the stock
	plt.bar(up.index, up.Close-up.Open, width, bottom=up.Open, color=col1)
	plt.bar(up.index, up.High-up.Close, width2, bottom=up.Close, color=col1)
	plt.bar(up.index, up.Low-up.Open, width2, bottom=up.Open, color=col1)
	
	# Plotting down prices of the stock
	plt.bar(down.index, down.Close-down.Open, width, bottom=down.Open, color=col2)
	plt.bar(down.index, down.High-down.Open, width2, bottom=down.Open, color=col2)
	plt.bar(down.index, down.Low-down.Close, width2, bottom=down.Close, color=col2)
	
	# rotating the x-axis tick labels at 30degree 
	# towards right
	
	
	
	title = 'nada niet'
	buy_price = []
	sell_price = []
	if len(trade) > 0:
		print(trade)
		
	buf = BytesIO()
	plt.savefig(buf, format="png")
	dat = base64.b64encode(buf.getbuffer()).decode("ascii")
	return render_template("base.html",title = title,dat = dat)

if __name__ == '__main__':
   app.run(debug = True)