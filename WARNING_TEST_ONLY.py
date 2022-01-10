from binance.client import Client
import config
from binance.enums import *

#DO NOT EXECUTE IN PROD PLS
#WARNING SELL ALL PAIR_B FOR PAIR_S !!!!!
client = Client(config.API_KEY, config.API_SECRET, tld='com')
client.API_URL = 'https://testnet.binance.vision/api'#test
    
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

if float(client.get_asset_balance(asset=config.PAIR_B.upper())['free'])>0:
        orders = client.get_open_orders(symbol=config.PAIR_M)
        for order in orders:
            client.cancel_order(symbol=config.PAIR_M,orderId=order['orderId'])
            #print(order)
        #print(client.get_symbol_info(config.PAIR_M)['filters'])
        #ask_price = client.get_orderbook_ticker(symbol=config.PAIR_M)['askPrice']
        print(client.get_orderbook_ticker(symbol=config.PAIR_M))
        while float(client.get_asset_balance(asset=config.PAIR_B.upper())['free']) > 100:
            ask_price = float(client.get_orderbook_ticker(symbol=config.PAIR_M)['askPrice'])
            order_succeeded = order(ask_price-0.01,SIDE_SELL,config.QUANTITY,config.PAIR_M,ask_price)
            if order_succeeded:
                print("!!!!!!!!! WARNING SELLING ALL PAIR_B FOR PAIR_S !!!!!!!!!!")
                print("XRP : ",client.get_asset_balance(asset=config.PAIR_B.upper())['free'])
                print("USDT : ",client.get_asset_balance(asset=config.PAIR_S.upper())['free'])