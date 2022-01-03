import websocket, json, config, aiofiles,pandas as pd,asyncio
from binance.client import Client
from binance.enums import *
from datetime import datetime

SOCKET = "wss://stream.binance.com:9443/ws/xrpusdt@kline_1m"

TRADE_SYMBOL = 'XRPUSDT'
TRADE_QUANTITY = 20

order_id = 0
in_position = False

async def save(tim,data):
    async with aiofiles.open('tst.csv', mode='r') as f:
        contents = await f.read()
        contents = contents+"\n"+str(datetime.utcfromtimestamp(tim/1000))+","+str(data['o'])+","+str(data['h'])+","+str(data['l'])+","+str(data['c'])
    async with aiofiles.open('tst.csv', mode='w') as f:
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

    print("----------Save-----------") 
    asyncio.run(save(json_message['E'],candle))
    print("-------------------------")

    
    print("---------Analyze---------") 

    data = pd.read_csv('tst.csv').set_index('Date')
    data.index = pd.to_datetime(data.index)

    # get price avg for 5-10-30 days
    sma_5 = pd.DataFrame(data['Close'].rolling(window=10).mean()).max()['Close']
    sma_10 = pd.DataFrame(data['Close'].rolling(window=20).mean()).max()['Close']

    data = data['Close']

    if(len(data)<50):# if less than 20 trade wait
        print("wait",len(data),"/50")
    else:
        print("current price :",data[-1])
        print("avg last 10 trade :",sma_5)
        print("avg last 20 trade :",sma_10)
      
        if data[-1] < sma_5: # if last price < last 10 trade's price avg = buy
            if in_position == False:
                order_succeeded = order(0,SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                if order_succeeded:
                    in_position = True
                    order_sell = order(round(data[-1]+data[-1]*0.0007,4),SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL) # sell at : buy price + 0.0007%
                    if order_sell:
                        print("success sell limit")
                    else:
                        print("fail sell limit")
                else:
                    print("fail buy")
            else:
                sorder = client.get_order(symbol=TRADE_SYMBOL,orderId=order_id)
                if sorder['status'] == 'FILLED':
                    print("restart please")
                    in_position = False
                else:  
                    print("waiting for sell : ",sorder)

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
