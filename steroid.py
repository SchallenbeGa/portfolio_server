import websocket, json, config, aiofiles,pandas as pd,asyncio
from binance.client import Client
from binance.enums import *
from datetime import datetime
from dateutil import tz
import time

SOCKET = "wss://stream.binance.com:9443/ws/"+config.PAIR+"@kline_1m"

TRADE_SYMBOL = config.PAIR_M
TRADE_QUANTITY = config.QUANTITY
TEST = config.DEBUG

order_id = 0
in_position = False
sell_price = 0

with open("tst.csv", "r") as f:
    data = f.readlines()

with open("tst.csv", "w") as f:
    for line in data :
        if line.strip("\n") == "Date,Open,High,Low,Close,Volume" : 
            f.write(line)


with open("trade.csv", "w") as f: 
    f.write("Date,Type,Price,Quantity\n")

with open("order.csv", "w") as f:
    f.write("Date,Type,Price,Quantity\n")

#save trade form the bot in trade.csv
async def save_trade(b_s,price):
    async with aiofiles.open('trade.csv', mode='r') as f:
        contents = await f.read()
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        contents = contents+str(str(current_time)+","+str(b_s)+","+str(price)+","+str(TRADE_QUANTITY)+"\n")
    async with aiofiles.open('trade.csv', mode='w') as f:
        await f.write(contents)

#save sell order form the bot in order.csv
async def save_order(price):
    async with aiofiles.open('order.csv', mode='w') as f:
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        print("here")
        await f.write("Date,Price,Quantity"+"\n"+str(str(current_time)+","+str(price)+","+str(TRADE_QUANTITY)))
        
async def save_data():
    klines = client_data.get_historical_klines(config.PAIR_M, Client.KLINE_INTERVAL_1MINUTE, "1 hour ago UTC")
    async with aiofiles.open('tst.csv', mode='w') as f:
        await f.write("Date,Open,High,Low,Close,Volume")
        for line in klines:
            await f.write(f'\n{datetime.fromtimestamp(line[0]/1000)}, {line[1]}, {line[2]}, {line[3]}, {line[4]},{line[5]}')

async def save_close(tim,data):
    async with aiofiles.open('tst.csv', mode='r') as f:
        contents = await f.read()
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        contents = contents+"\n"+str(current_time)+","+str(data['o'])+","+str(data['h'])+","+str(data['l'])+","+str(data['c'])+","+str(data['v'])
    async with aiofiles.open('tst.csv', mode='w') as f:
        await f.write(contents)

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
    
client = Client(config.API_KEY, config.API_SECRET, tld='com')
client_data = Client(config.API_KEY, config.API_SECRET, tld='com')
asyncio.run(save_data())
if TEST :
    client.API_URL = 'https://testnet.binance.vision/api'#test

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

PAIR_WITH = 'USDT'
QUANTITY = TRADE_QUANTITY
FIATS = ['EURUSDT', 'GBPUSDT', 'JPYUSDT', 'USDUSDT', 'DOWN', 'UP']
TIME_DIFFERENCE = 1
CHANGE_IN_PRICE = 1


def get_price():
    '''Return the current price for all coins on binance'''

    initial_price = {}
    prices = client.get_all_tickers()

    for coin in prices:

        # only Return USDT pairs and exlcude margin symbols like BTCDOWNUSDT
        if PAIR_WITH in coin['symbol'] and all(item not in coin['symbol'] for item in FIATS):
            initial_price[coin['symbol']] = { 'price': coin['price'], 'time': datetime.now()}

    return initial_price
initial_price = get_price()
def wait_for_price():
    global initial_price
    volatile_coins = {}
    last_price = get_price()

    # calculate the difference between the first and last price reads
    for coin in initial_price:
        threshold_check = (float(initial_price[coin]['price']) - float(last_price[coin]['price'])) / float(last_price[coin]['price']) * 100

        # each coin with higher gains than our CHANGE_IN_PRICE is added to the volatile_coins dict
        if threshold_check > CHANGE_IN_PRICE:
            volatile_coins[coin] = threshold_check
            volatile_coins[coin] = round(volatile_coins[coin], 3)

            print(f'{coin} has gained {volatile_coins[coin]}% in the last minutes, calculating volume in {PAIR_WITH}')

    if len(volatile_coins) < 1:
            print(f'No coins moved more than {CHANGE_IN_PRICE}% in the last minute(s)')
    return volatile_coins, len(volatile_coins), last_price


def on_message(ws, message):
    global in_position,order_id,sell_price,initial_price

    json_message = json.loads(message)  
    candle = json_message['k']
    is_candle_closed = candle['x']
    if (is_candle_closed):
        thecoins, thecoins_l,last_p = wait_for_price()
    #asyncio.run(save_data())
    #asyncio.run(save_close(json_message['E'],candle))
    data = pd.read_csv('tst.csv').set_index('Date')
    data.index = pd.to_datetime(data.index)

    sma = data['Close'][-8:].mean()
    close = float(candle['c'])

    print("current price :",close)
    print("cross price   :",sma)

    if in_position:
        sorder = client.get_order(symbol=TRADE_SYMBOL,orderId=order_id)
        if TEST:
            print("Ready")
            if sell_price<=close:
                print("selll")
                print("cross price :",sma)
                print(sorder['price'])
                asyncio.run(save_trade("sell",sorder['price']))
                print('\a')
                print('\a')
                in_position = False
                with open("order.csv", "w") as f:
                    f.write("Date,Type,Price,Quantity\n")
            else:
                print("need higher price")
        else: 
            if sorder['status'] == 'FILLED':
                print("cross price :",sma)
                print(sorder['price'])
                asyncio.run(save_trade("sell",sorder['price']))
                print('\a')
                print('\a')
                in_position = False
            else:  
                print("waiting for sell : ",sorder)
 
    if (close < sma):# if last price < last 10 trade's price avg = buy
        if in_position == False:
            order_succeeded = order(0,SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
            if order_succeeded:
                in_position = True
                print("here")
                asyncio.run(save_trade("buy",close))
                print("hoo")
                print('\a')
                sell_price = close+0.002
                order_sell = order(close+0.002,SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL) # sell at : buy price + 0.0005%
                if order_sell:
                    print("here")
                    asyncio.run(save_order(close+0.002))
                    print("success sell limit")
                else:
                    print("fail sell limit")
            else:
                print("fail buy")
    
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()