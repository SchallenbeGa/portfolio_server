import dash
import datetime
import pandas as pd
import plotly.graph_objects as go
from dash import dcc
from dash import html
from pycoingecko import CoinGeckoAPI
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

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

	low_avg = df['Low'].mean()
	high_avg = df['High'].mean()
	high_avg -= (high_avg/100)*2 # 2% less 
	low_avg -= (low_avg/100)*3 # 3% less

	low = df.min()['Low']
	high = df.max()['High']

	x0 = df.at[0,'Date']
	x1 = df.at[df.last_valid_index(),'Date']


	fig = go.Figure(data=[go.Candlestick(x=df['Date'],
		open=df['Open'],
		high=df['High'],
		low=df['Low'],
		close=df['Close'])],
	)
	fig.add_shape(type="line",
    	x0=x0, x1=x1, y0=low_avg, y1=low_avg,
		line=dict(
			color="green",
			width=2,
			dash="dot",
		)
	)
	fig.add_shape(type="line",
    	x0=x0, x1=x1, y0=high_avg, y1=high_avg,
		line=dict(
			color="red",
			width=2,
			dash="dot",
		)
	)
	fig.add_shape(type="line",
    	x0=x0, x1=x1, y0=low, y1=low,
		line=dict(
			color="limegreen",
			width=2,
			dash="dot",
		)
	)
	fig.add_shape(type="line",
    	x0=x0, x1=x1, y0=high, y1=high,
		line=dict(
			color="salmon",
			width=2,
			dash="dot",
		)
	)
	return fig


save(req(money,days))
fig = set_figure(pd.read_csv('tst.csv'))

app = dash.Dash(__name__)
app.layout = html.Div(
    [		
		dcc.Graph(style={'width': '100%', 'height': '400px'},figure=fig,id='live-update-graph'),
		dcc.Input(id='input-on-submit', type='text',value="ripple"),
    	html.Button('Submit', id='submit-val', n_clicks=0),
		dcc.Dropdown(
        id='demo-dropdown',
        options=[
            {'label': '1 Days', 'value': '1'},
            {'label': '7 Days', 'value': '7'},
            {'label': '30 Days', 'value': '30'}
        ],
        value='1'
		)
	]
)

@app.callback(
	Output('live-update-graph', 'figure'),
   	Input('submit-val', 'n_clicks'),
	Input('demo-dropdown', 'value'),
    dash.dependencies.State('input-on-submit', 'value')
)


def update_output(n_clicks, value,val):
	if n_clicks is None :
		raise PreventUpdate
	elif(val==None):
		raise PreventUpdate
	else:	
		return update_graph_live(val,value)

def update_graph_live(currency="bitcoin",days=1):
	save(req(currency,days))
	return set_figure( pd.read_csv('tst.csv'))

if __name__ == "__main__":
    app.run_server(debug=True)