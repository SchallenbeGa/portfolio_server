import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import datetime
from flask import Flask,render_template,redirect

app = Flask(__name__)

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

@app.route('/')
def home():
	data = pd.read_csv('tst.csv').set_index('Date')
	data.index = pd.to_datetime(data.index)

	plt.close()
	f = plt.figure()
	f.set_figwidth(15)
	f.set_figheight(7)

	plt.plot(data['Close'], alpha = 0.3, label = 'data')

	plt.legend(loc = 'upper left')

	title = 'nada niet'

	buf = BytesIO()
	plt.savefig(buf, format="png")
	dat = base64.b64encode(buf.getbuffer()).decode("ascii")

	return render_template("base.html",dat = dat)


if __name__ == '__main__':
   app.run(debug = True)