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

SOCKET = "wss://stream.binance.com:9443/ws/xrpbnb@kline_1m"

TRADE_SYMBOL = 'XRPBNB'
TRADE_QUANTITY = 50

order_id = 0
in_position = False

#save trade form binance in tst.csv
async def save(tim,data):
    async with aiofiles.open('tst.csv', mode='r') as f:
        contents = await f.read()
        contents = contents+"\n"+str(datetime.utcfromtimestamp(tim/1000))+","+str(data['o'])+","+str(data['h'])+","+str(data['l'])+","+str(data['c'])
    async with aiofiles.open('tst.csv', mode='w') as f:
        await f.write(contents)
#save trade form the bot in trade.csv
async def save_trade(b_s,price):
    async with aiofiles.open('trade.csv', mode='r') as f:
        contents = await f.read()
        contents = contents+"\n"+str(str(b_s)+","+str(price))
    async with aiofiles.open('trade.csv', mode='w') as f:
        await f.write(contents)

client = Client(config.API_KEY, config.API_SECRET, tld='com')

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
    global closes, in_position,order_id

    json_message = json.loads(message)
    candle = json_message['k']

    asyncio.run(save(json_message['E'],candle))

    data = pd.read_csv('tst.csv').set_index('Date')
    data.index = pd.to_datetime(data.index)

    if(len(data)<300):# if less than 30 trade wait
        print("wait",len(data),"/30")
    else:
        # get price avg for 5-10-30 days
        #print(pd.DataFrame(data['Close'][-20:].rolling(window=10).mean()))
        #sma_5 = pd.DataFrame(data['Close'][-30:].rolling(window=10).mean()).max()['Close']

        data = data['Close']

        sma_5 = pd.DataFrame(data['Close'][-30:].rolling(window=10).mean()).max()['Close']

        print("current price :",data[-1])
        print("cross price   :",sma_5*0.01)
         

        if data[-1] > sma_5: # if last price < last 10 trade's price avg = buy
            if in_position == False:
                order_succeeded = order(0,SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                if order_succeeded:
                    in_position = True
                    asyncio.run(save_trade("buy",data[-1]))
                    print('\a')
                    order_sell = order(round(data[-1]+data[-1]*0.005,5),SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL) # sell at : buy price + 0.0005%
                    if order_sell:
                        print("success sell limit")
                    else:
                        print("fail sell limit")
                else:
                    print("fail buy")
            else:
                sorder = client.get_order(symbol=TRADE_SYMBOL,orderId=order_id)
                if sorder['status'] == 'FILLED':
                    print("cross price :",sma_5)
                    if(data[-1]<sma_5):
                        print(sorder['price'])
                        asyncio.run(save_trade("sell",sorder['price']))
                        print('\a')
                        print('\a')
                        in_position = False
                else:  
                    print("waiting for sell : ",sorder)

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
