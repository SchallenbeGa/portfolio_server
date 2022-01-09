import pandas as pd
import numpy as np
import base64
import config
from io import BytesIO
import datetime
import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go

data = pd.read_csv('tst.csv')
trade = pd.read_csv('trade.csv')
trade_d = trade
trade.set_index('Date')

buf = BytesIO()
fees = 0	
order = pd.read_csv('order.csv')
fig = go.Figure() # or any Plotly Express function e.g. px.bar(...)
# fig.add_trace( ... )
# fig.update_layout( ... )

fig = go.Figure(data=[go.Candlestick(x=data['Date'],
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'])])

app = dash.Dash()
print(html.Div([
    dcc.Graph(figure=fig)
])
)
app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter