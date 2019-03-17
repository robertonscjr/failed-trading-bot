from exchange.poloniex import Poloniex
from utils import conf
import os
import time 
import datetime

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
    tickers = client.returnTicker().keys()
    pairs = []
    balance = client.returnBalances()
    number_of_orders = 5 
    order_book = client.returnOrderBook('BTC_RIC',
						  number_of_orders)
    history = client.marketTradeHist('BTC_EXP')

    sell_history = history[0]
    sell_orders = order_book['asks'] 
    value_orders = []
    
     
    print" %s (%s)" % (sell_history['rate'],sell_history['date'])
    for order in sell_orders:
        value_orders.append(float(order[0]))
    
    for k in range(0,3):
        d = []
	#print"value order: %.8f" % value_orders[k]
    for pair in tickers :
	timestamp = time.time() 
	timestamp_range = timestamp - (900 * 5)
	candle = client.returnChartData(pair, 900, timestamp_range,timestamp)
	have_gigante = candle_gigante(candle, pair)
	#have_hammer  = candle_hammer(candle)
	if(have_gigante):
	    print"(%s) FOUND GIGANTE !!" % pair
