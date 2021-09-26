import dash
import datetime
import pandas as pd
import plotly.graph_objects as go
from dash import dcc
from dash import html
from pycoingecko import CoinGeckoAPI
from dash.dependencies import Input, Output

fig = go.Figure()
cg = CoinGeckoAPI()
app = dash.Dash()

days = "1"
money = "ripple"

def req(money="ripple",days=1):
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

def set_figure(df):
	return go.Figure(data=[go.Candlestick(x=df['Date'],
		open=df['Open'],
		high=df['High'],
		low=df['Low'],
		close=df['Close'])])


save(req(money,days))
fig = set_figure(pd.read_csv('tst.csv'))

app = dash.Dash(__name__)
app.layout = html.Div(
    [
		dcc.Graph(figure=fig,id='live-update-graph'),
		dcc.Input(id='input-on-submit', type='text'),
    	html.Button('Submit', id='submit-val', n_clicks=0),
    	html.Div(id='container-button-basic',
             children='Enter a value and press submit')
    ]
)

@app.callback(
	Output('live-update-graph', 'figure'),
   	Input('submit-val', 'n_clicks'),
    dash.dependencies.State('input-on-submit', 'value')
)

def update_output(n_clicks, value):
	if value :
		return update_graph_live(value)
	else : return set_figure( pd.read_csv('tst.csv'))

def update_graph_live(currency="bitcoin"):
	try :
		save(req(currency))
		return set_figure( pd.read_csv('tst.csv'))
	except:
		save(req("bitcoin"))
		return set_figure( pd.read_csv('tst.csv'))

if __name__ == "__main__":
    app.run_server(debug=True)