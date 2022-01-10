import websocket, json, config
from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/"+config.PAIR+"@kline_1m"

#DO NOT EXECUTE IN PROD PLS
#WARNING SELL ALL PAIR_B FOR PAIR_S !!!!!
client = Client(config.API_KEY, config.API_SECRET, tld='com')
client.API_URL = 'https://testnet.binance.vision/api'#test

order_id = 0
in_position = False

def order(limit,side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    global order_id
    try:
        if limit > 0:
            order = client.create_order(symbol=symbol,side=side,type=ORDER_TYPE_LIMIT,quantity=config.QUANTITY,price=limit,timeInForce=TIME_IN_FORCE_GTC)
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
    # get balances for all assets & some account information
    global in_position,order_id
    json_message = json.loads(message)  
    candle = json_message['k']
    if in_position :
        sorder = client.get_order(symbol=config.PAIR_M,orderId=order_id)
        if sorder['status'] == 'FILLED':
            in_position = False
        else:
            print("-----------waiting-------------")
            print(sorder)
    else:
        if float(client.get_asset_balance(asset=config.PAIR_B.upper())['free'])>0:
            print(client.get_orderbook_ticker(symbol=config.PAIR_M))
            #ask_price = float(client.get_orderbook_ticker(symbol=config.PAIR_M)['askPrice'])
            order_succeeded = order(float(candle['c']),SIDE_SELL,config.QUANTITY,config.PAIR_M)
            if order_succeeded:
                print("!!!!!!!!! WARNING SELLING ALL PAIR_B FOR PAIR_S !!!!!!!!!!")
                print("XRP : ",client.get_asset_balance(asset=config.PAIR_B.upper())['free'])
                print("USDT : ",client.get_asset_balance(asset=config.PAIR_S.upper())['free'])
                in_position = True
            else:
                print("something went wrong")
    
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()