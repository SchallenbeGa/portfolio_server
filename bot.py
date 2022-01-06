import websocket, json, config, aiofiles,pandas as pd,asyncio
from binance.client import Client
from binance.enums import *
from datetime import datetime

with open("trade.csv", "r") as f:
    data = f.readlines()

with open("trade.csv", "w") as f:
    for line in data :
        if line.strip("\n") == "Date,Type,Price,Quantity" : 
            f.write(line)

SOCKET = "wss://stream.binance.com:9443/ws/"+config.PAIR+"@kline_1m"

TRADE_SYMBOL = config.PAIR_M
TRADE_QUANTITY = config.QUANTITY

order_id = 0
in_position = False

#save trade form the bot in trade.csv
async def save_trade(date_t,b_s,price):
    async with aiofiles.open('trade.csv', mode='r') as f:
        contents = await f.read()
        contents = contents+"\n"+str(str(datetime.utcfromtimestamp(date_t/1000))+","+str(b_s)+","+str(price)+","+str(TRADE_QUANTITY))
    async with aiofiles.open('trade.csv', mode='w') as f:
        await f.write(contents)

client = Client(config.API_KEY, config.API_SECRET, tld='com')
client.API_URL = 'https://testnet.binance.vision/api'#test

def order(limit,side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    global order_id
    try:
        if limit > 0:
            print("test")
            order = client.create_order(symbol=symbol,side=side,type=ORDER_TYPE_LIMIT,quantity=TRADE_QUANTITY,price=limit,timeInForce=TIME_IN_FORCE_GTC)
        else:
            order = client.create_order(symbol=symbol,side=side,type=order_type, quantity=quantity)
        print("sending order")
        print(order)
        order_id = order['orderId']
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True
    
def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):

    global in_position,order_id

    json_message = json.loads(message)  
    candle = json_message['k']
    
    data = pd.read_csv('tst.csv').set_index('Date')
    data.index = pd.to_datetime(data.index)

    sma = pd.DataFrame(data['Close'][-15:].rolling(window=10).mean()).max()['Close']

    close = float(candle['c'])

    print("current price :",close)
    print("cross price   :",sma)
        
    if close > sma :# if last price < last 10 trade's price avg = buy
        if in_position == False:
            order_succeeded = order(0,SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
            if order_succeeded:
                in_position = True
                asyncio.run(save_trade(datetime.now().timestamp()*1000,"buy",close))
                print('\a')
                order_sell = order(close+0.001,SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL) # sell at : buy price + 0.0005%
                if order_sell:
                    print("success sell limit")
                else:
                    print("fail sell limit")
            else:
                print("fail buy")
        else:
            sorder = client.get_order(symbol=TRADE_SYMBOL,orderId=order_id)
            if sorder['status'] == 'FILLED':
                print("cross price :",sma)
                if(close<sma):
                    print(sorder['price'])
                    asyncio.run(save_trade(sorder['time'],"sell",sorder['price']))
                    print('\a')
                    print('\a')
                    in_position = False
            else:  
                print("waiting for sell : ",sorder)

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()