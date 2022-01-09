import websocket, json, config, aiofiles, asyncio
from binance.client import Client
from binance.enums import *
from datetime import datetime

SOCKET = "wss://stream.binance.com:9443/ws/"+config.PAIR+"@kline_1m"

order_id = 0
in_position = False
sell_price = 0

async def save(tim,data):

    klines = client.get_historical_klines(config.PAIR_M, Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
    print(klines)
    async with aiofiles.open('tst.csv', mode='w') as f:
        await f.write("Date,Open,High,Low,Close,Volume")
        for line in klines:
            await f.write(f'\n{datetime.utcfromtimestamp(line[0]/1000)}, {line[1]}, {line[2]}, {line[3]}, {line[4]},{line[5]}')

client = Client(config.API_KEY, config.API_SECRET, tld='com')
    
def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, in_position,order_id,sell_price

    json_message = json.loads(message)
    candle = json_message['k']
    is_candle_closed = candle['x']
    asyncio.run(save(json_message['E'],candle))
    if is_candle_closed:
        print("----------Save-----------") 
        
        print("-------------------------")
    else:
        print("waiting for candle to close")

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
