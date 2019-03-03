from binance.client import Client
import matplotlib.pyplot as plt
from datetime import datetime
import time

api_key = 'key'
api_secret = 'secret'

client = None
while not client:
    try:
        client = Client(api_key, api_secret)
    except:
        pass

print("client ok")

def get_buysell_relation():
    symbol = 'ETHBTC'
    trades = client.get_recent_trades(symbol=symbol)[400:]
    ticker = client.get_orderbook_ticker(symbol=symbol)
    
    times = [int(float(trade['time'])/1000) for trade in trades]
    prices = [trade['price'] for trade in trades]
    order_types = [trade['isBuyerMaker'] for trade in trades]
    volume = [trade['qty'] for trade in trades]
    
    #for i in range(0, 500):
    #    print "%.6f - %.3f - %s - %s" % (float(prices[i]), float(volume[i]),
    #        datetime.utcfromtimestamp(times[i]).strftime('%H:%M:%S'),
    #        order_types[i])
    
    buy_orders = 0 # BUY ORDERS abaixam o valor da moeda
    sell_orders = 0 # SELL ORDERS aumentam o valor da moeda
    
    for order in order_types:
        if order:
            buy_orders = buy_orders + 1
        else:
            sell_orders = sell_orders + 1

    ratio = (float(sell_orders) / float(buy_orders))*100-100

    sell_price = float(ticker['askPrice'].encode('utf-8'))
    buy_price = float(ticker['bidPrice'].encode('utf-8'))
    with open('log', 'a+') as log_file:
        log_file.write("%s - %.1f - %.6f - %.6f\n" % (get_time(),
            ratio, sell_price, buy_price))

        print("%s - tape: %.1f - sell: %.6f - buy: %.6f" % (get_time(),
        ratio, sell_price, buy_price))

def get_time():
    return datetime.utcfromtimestamp(time.time()-10800).strftime('%H:%M:%S')

for i in range(0, 1000):
    time.sleep(3) 
    try:
        get_buysell_relation()

    except Exception as e:

        import pdb; pdb.set_trace()
