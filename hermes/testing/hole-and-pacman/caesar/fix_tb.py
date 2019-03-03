from exchange.poloniex import Poloniex
from utils import conf
import os
import time 
import datetime
from buy_action import Buy_action
def candle_size(candle): 
    open_candle = float(candle['open'])
    close_candle = float(candle['close'])
	
    return ((close_candle / open_candle)-1.0) * 100
    
def candle_gigante(candle, pair):
    try:
        first_candle = candle_size(candle[len(candle) -1])
        second_candle = candle_size(candle[len(candle) -2])
    except:
	print'(%s) ERROR' % pair
        return False
    if (first_candle > 0) and (second_candle < 0) \
                          and (first_candle > (2 * abs(second_candle) )):
        return True       
    
def candle_hammer(candle):
    first_candle = candle_size(candle[len(candle) - 1])
    second_candle = candle_size(candle[len(candle) -2])
	
    open_candle = float(candle[len(candle) -1]['open'])
    head = float(candle[len(candle) -1]['high'])
    tail = float(candle[len(candle) -1]['low'])

    if (first_candle > 0) and (second_candle < 0) \
                 	  and (open_candle > tail*1.4):
        return True       
if __name__ == "__main__":
    client = Poloniex(conf.api_key, conf.secret)
    tickers = client.returnTicker()['BTC_NEOS']
    pairs = []
    balance = client.returnBalances()
    number_of_orders = 10 
    order_book = client.returnOrderBook('BTC_NEOS',
						  number_of_orders)
    history = client.marketTradeHist('BTC_NEOS')
    sell_history = []
    
    change = tickers['percentChange']
    print "percent change: %.8f" % float(change)
    for k in range(0,10):
        sell_history.append(history[k])     
        print" %s (%s) (%s)" % (sell_history[k]['rate'],sell_history[k]['date'],sell_history[k]['type'])
    
    sell_orders = order_book['asks'] 
    value_orders = []  
    
    for order in sell_orders:
        value_orders.append(float(order[0]))
    
    for i in reversed(range(number_of_orders - 1)):
        if value_orders[i + 1] - value_orders[i] > 0.00000050:
            price_to_sell = value_orders[i + 1]
	    print"value order: %.8f" % value_orders[i]
   
    run = Buy_action(client,'BTC_NEOS',0.0001)
    run.start()

