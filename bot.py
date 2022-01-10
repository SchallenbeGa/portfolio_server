import websocket, json, base64, config, aiofiles,pandas as pd,asyncio,numpy as np,mplfinance as mpf
from binance.client import Client
from binance.enums import *
from binance.helpers import round_step_size
from datetime import datetime
from io import BytesIO

#https://developer.twitter.com/
#https://developer.twitter.com/en/apps
#click on app and write "auth-settings" in url,
#https://developer.twitter.com/en/portal/projects/xxxx/apps/xxxx/ <- !auth-settings
#oauth 1.0a put on
#Callback URI / Redirect URL -> http://twitter.com
#Website URL -> http://twitter.com
#save
import tweepy

consumer_key = config.C_KEY
consumer_secret = config.C_SECRET
access_token = config.A_T
access_token_secret = config.A_T_S

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

SOCKET = "wss://stream.binance.com:9443/ws/"+config.PAIR+"@kline_1m"

TRADE_SYMBOL = config.PAIR_M
TRADE_QUANTITY = config.QUANTITY
TEST = config.DEBUG

sma_d = 2
sma_l = 3
added_val = 0.0001
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


##tweet graph img
async def twet_graph(tweet_content,fav):
    global api,sma_d
    print("start graph")
    data = pd.read_csv('tst.csv').set_index('Date')
    data.index = pd.to_datetime(data.index,format="%Y-%m-%d %H:%M:%S")
    trade = pd.read_csv('trade.csv')
    trade_d = trade
    trade.set_index('Date')
    buf = BytesIO()
    fees = []	
    gains = []
    s  = mpf.make_mpf_style(base_mpf_style="yahoo",facecolor="#282828",gridcolor="#212121",rc={'xtick.color':'#f8f8f8','ytick.color':'#f8f8f8','axes.labelcolor':'#f8f8f8'})
    if len(trade)>0 :
        
        buy = []
        sell = []
        trade_f = []
        for x in range(len(trade)):
            if len(trade)>1:
                if(x<=len(trade)-2):
                    print(trade['Price'][x])
                    gains.append(trade['Price'][x+1]*int(config.QUANTITY)-trade['Price'][x]*int(config.QUANTITY))
            fees.append(((trade['Price'][x]*int(config.QUANTITY))/100)*0.1)
            trade_f.append(datetime.strptime(trade_d['Date'][x],"%Y-%m-%d %H:%M:%S").minute)

        for i in range(len(data)):
            is_done = False
            if data.index.array[i].minute in trade_f:
                print("maybe")
                for x in range(len(trade)):
                    if((data.index.array[i].minute==datetime.strptime(trade_d['Date'][x],"%Y-%m-%d %H:%M:%S").minute) & (data.index.array[i].hour==datetime.strptime(trade_d['Date'][x],"%Y-%m-%d %H:%M:%S").hour)):
                        print("start")
                        is_done = True
                        print(data['Low'][i])
                        print(trade['Price'][x])	
                        if(trade['Type'][x]=="buy"):
                            buy.append(trade['Price'][x]-0.002)
                        else:
                            sell.append(trade['Price'][x]+0.002)
            if not is_done:
                buy.append(np.nan)
                sell.append(np.nan)
        
        for x in range(int((len(trade)-2)/2)):
            buy.append(np.nan)
            sell.append(np.nan)

        if len(data)>len(buy):
            buy.append(np.nan)
            sell.append(np.nan)
        
        sell_n = 0
        for v in sell :              
            if not np.isnan(v):     
                sell_n+=1

        if sell_n>0:
            sell.append(np.nan)
            apd = [
                mpf.make_addplot(buy, scatter=True, markersize=200, marker=r'^', color='green'),
                mpf.make_addplot(sell, scatter=True, markersize=200, marker=r'v', color='red')
            ]
        else:
            apd = [mpf.make_addplot(buy, scatter=True, markersize=200, marker=r'^', color='green')]
            print("py")
        fig,ax = mpf.plot(
            data,
            addplot=apd,
            type='candle',
            volume=True,
            style=s,
            mav=(8,10),
            figscale=1,
            figratio=(20,10),
            datetime_format="%d %H:%M:%S",
            xrotation=0,
            returnfig=True)
        fig.savefig('tweettest.png',facecolor='#282828')
    else:
        fig,ax = mpf.plot(
            data,
            type='candle',
            volume=True,
            style=s,
            mav=(8,10),
            figratio=(20,10),
            datetime_format="%d %H:%M:%S",
            xrotation=0,
            returnfig=True)
        fig.savefig('tweettest.png',facecolor='#282828')
    print("save graph")
    order = pd.read_csv('order.csv')
    dat = base64.b64encode(buf.getbuffer()).decode("ascii")

    id = api.update_status_with_media(tweet_content,"tweettest.png").id
    if fav:
        api.create_favorite(id)
    return id

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

async def save_close(data):
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

def on_message(ws, message):
    global in_position,order_id,sell_price,api,added_val,sma_d,sma_l
    # get balances for all assets & some account information
    json_message = json.loads(message)  
    candle = json_message['k']
    is_candle_closed = candle['x']

    asyncio.run(save_data())

    #asyncio.run(save_close(json_message['E'],candle))
    data = pd.read_csv('tst.csv').set_index('Date')
    data.index = pd.to_datetime(data.index)

    sma = data['Close'][-sma_d:].mean()
    sma_long = data['Close'][-sma_l:].mean()
    close = float(candle['c'])

    if (is_candle_closed):
        if in_position:
            if data['Close'][-1]-(sell_price-added_val) <0:
                print((data['Close'][-1]*float(TRADE_QUANTITY))-((sell_price-added_val)*float(TRADE_QUANTITY)))
                tweet = "buy at : "+str(sell_price-added_val)+"\nquantity("+config.PAIR_B+") : "+str(TRADE_QUANTITY)+"\nlast price : "+str(data['Close'][-1])+"\nactual loss : -"+str(((sell_price-added_val)*float(TRADE_QUANTITY))-(data['Close'][-1]*float(TRADE_QUANTITY)))
            else:
                tweet = "buy at : "+str(sell_price-added_val)+"\nquantity("+config.PAIR_B+") : "+str(TRADE_QUANTITY)+"\nlast price : "+str(data['Close'][-1])+"\nactual profit : "+str((data['Close'][-1]*float(TRADE_QUANTITY))-((sell_price-added_val)*float(TRADE_QUANTITY)))
            tweet+="\nsell limit at : "+str(sell_price)
            #twet_graph(tweet)
       #else:
        #    twet_graph("waiting... need to cross blue line\nactual price : "+str(data['Close'][-1])+"\ncross price : "+str(sma))

    print("current price :",close)
    print("lower than : ",sma_long," higher than : ",sma)

    if in_position:
        sorder = client.get_order(symbol=TRADE_SYMBOL,orderId=order_id)
        if TEST:
            if sell_price<=close:
                #asyncio.run(save_close(candle))
                tweet = "buy at :"+str(sell_price-added_val)+"\nsell at : "+str(close)+"\nprofit : "+str((close*float(TRADE_QUANTITY))-((sell_price-added_val)*float(TRADE_QUANTITY)))
                print("cross price :",sma)
                print(sorder['price'])
                asyncio.run(save_trade("sell",sorder['price']))
                print('\a')
                print('\a')
                in_position = False
                asyncio.run(twet_graph(tweet,True))
                with open("order.csv", "w") as f:
                    f.write("Date,Type,Price,Quantity\n")
        else: 
            if sorder['status'] == 'FILLED':
                print("cross price :",sma)
                print(sorder['price'])
                asyncio.run(save_trade("sell",sorder['price']))
                in_position = False
            else:  
                print("waiting for sell : ",sorder)
 
    if (close < sma_long) & (close > sma):# if last price < last 10 trade's price avg = buy
        if in_position == False:
            order_succeeded = order(0,SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
            if order_succeeded:
                in_position = True
                tweet = "buy at : "+str(close)+"\nsell limit at : "+str(close+added_val)
               #api.update_status(tweet)
                asyncio.run(save_trade("buy",close))
                sell_price = close+added_val
                print(tweet)
                lim = round_step_size(close + added_val,float(client.get_symbol_info(config.PAIR_M)['filters'][0]["tickSize"]))
                order_sell = order(lim,SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL) # sell at : buy price + added_val
                if order_sell:
                    asyncio.run(save_order(close+added_val))
                    asyncio.run(twet_graph(tweet,False))
                    print("success sell limit")
                else:
                    print("fail sell limit")
            else:
                print("fail buy")
    
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
