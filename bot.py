import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *
import aiofiles
import numpy as np
import pandas as pd
import asyncio
from aiocsv import AsyncWriter
from datetime import datetime

SOCKET = "wss://stream.binance.com:9443/ws/xrpusdt@kline_1m"

TRADE_SYMBOL = 'XRPUSDT'
TRADE_QUANTITY = 20
signal = 1
last_buy = 0
closes = []
in_position = False

async def save(tim,data):

    async with aiofiles.open('tst.csv', mode='r') as f:
        contents = await f.read()
        contents = contents+"\n"+str(datetime.utcfromtimestamp(tim/1000))+","+str(data['o'])+","+str(data['h'])+","+str(data['l'])+","+str(data['c'])
    async with aiofiles.open('tst.csv', mode='w') as f:
        await f.write(contents)

client = Client(config.API_KEY, config.API_SECRET, tld='com')

def order(limit,side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
	if limit > 0:
		order = client.order_limit_sell(symbol=symbol,quantity=100,price=limit)
	else:
        	order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
	print("sending order")
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True

def sma(data, n):
	sma = data.rolling(window=n).mean()
	return pd.DataFrame(sma)
    
def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, in_position, signal, last_buy
    
    print('received message')
    json_message = json.loads(message)

    candle = json_message['k']
    is_candle_closed = candle['x']
    close = candle['c']
    print("----------Save-----------") 
    asyncio.run(save(json_message['E'],candle))
    print("-------------------------")

    
    print("---------Analyze---------") 
    data = pd.read_csv('tst.csv').set_index('Date')
    data.index = pd.to_datetime(data.index)

    print("okdata")

    n = [5,10,15]
    for i in n:
        data[f'sma_{i}'] = sma(data['Close'], i)

    sma_10 = data['sma_5']
    sma_20 = data['sma_10']
    sma_30 = data['sma_15']
  
    sma1 = sma_10
    sma2 = sma_20

    data = data['Close']

    print("Signal :",signal)
    if(len(data)<20):
        print("wait",len(data),"/20")
    else:
        print(sma1[-1])
        print(sma2[-1])
        
    if sma1[-1] > sma2[-1]:
        if signal>0:
		order = client.order_limit_sell(
    symbol='BNBBTC',
    quantity=100,
    price='0.00001')
            order_succeeded = order(0,SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
            if order_succeeded:
                print("buy price : ",data[-1])
                last_buy = data[-1]
                signal-=1
		order_sell = order(last_buy+last_buy*0.003,SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
		if order_sell:
			print("success sell limit")
		else:
			print("fail sell limit)
            else:
                print("fail buy")
        else:
            print("waiting for sell")
    elif sma2[-1] > sma1[-1]:
        if signal < 1:
            if last_buy<data[-1]:
                order_succeeded = order(0,SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                if order_succeeded:
                    print("sell price : ",data[-1])
                    signal+=1
                else:
                    print("fail buy")
            else:
                print("need higher price")
    print("-------------------------")
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
