import websocket, json, config, aiofiles,pandas as pd,asyncio
from binance.client import Client
from binance.enums import *
from datetime import datetime

#forsamimagain
with open("tst.csv", "r") as f:
    data = f.readlines()

with open("tst.csv", "w") as f:
    for line in data :
        if line.strip("\n") == "Date,Open,High,Low,Close,Volume" : 
            f.write(line)

with open("trade.csv", "r") as f:
    data = f.readlines()

with open("trade.csv", "w") as f:
    for line in data :
        if line.strip("\n") == "type,price" : 
            f.write(line)


SOCKET = "wss://stream.binance.com:9443/ws/xrpusdt@kline_1m"

TRADE_SYMBOL = 'XRPUSDT'
TRADE_QUANTITY = 50

order_id = 0
in_position = False
sell_price = 0

async def save(tim,data):
    async with aiofiles.open('tst.csv', mode='r') as f:
        contents = await f.read()
        contents = contents+"\n"+str(datetime.utcfromtimestamp(tim/1000))+","+str(data['o'])+","+str(data['h'])+","+str(data['l'])+","+str(data['c'])
    async with aiofiles.open('tst.csv', mode='w') as f:
        await f.write(contents)

async def save_trade(b_s,price):
    async with aiofiles.open('trade.csv', mode='r') as f:
        contents = await f.read()
        contents = contents+"\n"+str(str(b_s)+","+str(price))
    async with aiofiles.open('trade.csv', mode='w') as f:
        await f.write(contents)

client = Client(config.API_KEY, config.API_SECRET, tld='com')
    
def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, in_position,order_id,sell_price

    json_message = json.loads(message)
    candle = json_message['k']

    print("----------Save-----------") 
    asyncio.run(save(json_message['E'],candle))
    print("-------------------------")

    
    print("---------Analyze---------") 

    data = pd.read_csv('tst.csv').set_index('Date')
    data.index = pd.to_datetime(data.index)

    sma_5 = pd.DataFrame(data['Close'][-20:].rolling(window=15).mean()).max()['Close']
    sma_10 = pd.DataFrame(data['Close'][-30:].rolling(window=20).mean()).max()['Close']

    data = data['Close']
    print("current price :",data[-1])
    print("avg last 10 trade :",sma_5)
    print("avg last 20 trade :",sma_10)
    
    if data[-1] > sma_5: # if last price < last 10 trade's price avg = buy
        if in_position == False:
            asyncio.run(save_trade("buy",data[-1]))
            sell_price = data[-1]+data[-1]*0.0005
            in_position = True
        else:
            if data[-1] >= sell_price:                   
                asyncio.run(save_trade("sell",sell_price))
                in_position = False
            else:  
                print("waiting for sell at : ",sell_price)

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
