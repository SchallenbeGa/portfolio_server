import websocket, json, config, aiofiles, asyncio
from binance.client import Client
from binance.enums import *
from datetime import datetime

with open("tst.csv", "r") as f:
    data = f.readlines()

with open("tst.csv", "w") as f:
    for line in data :
        if line.strip("\n") == "Date,Open,High,Low,Close,Volume" : 
            f.write(line)

SOCKET = "wss://stream.binance.com:9443/ws/"+config.PAIR+"@kline_1m"

order_id = 0
in_position = False
sell_price = 0

async def save(tim,data):
    async with aiofiles.open('tst.csv', mode='r') as f:
        contents = await f.read()
        contents = contents+"\n"+str(datetime.utcfromtimestamp(tim/1000))+","+str(data['o'])+","+str(data['h'])+","+str(data['l'])+","+str(data['c'])+","+str(data['v'])
    async with aiofiles.open('tst.csv', mode='w') as f:
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
    is_candle_closed = candle['x']
    if is_candle_closed:
        print("----------Save-----------") 
        asyncio.run(save(json_message['E'],candle))
        print("-------------------------")
    else:
        print("waiting for candle to close")

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
