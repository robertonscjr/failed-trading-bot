from exchange.poloniex import Poloniex
from utils import conf
import os
import time
import datetime
import numpy as np
import pandas.io.data as web
import pandas as pd
    
def ema(chart_data, period):
    for k in range(1,len(chart_data)):
        chart_data_organized.append(chart_data[k-1]['close'])
    
    alpha = 2/(period +1.0)
    alpha_rev = 1-alpha
    chart_data_fl = np.array(chart_data_organized,dtype=float)
    n = chart_data_fl.shape[0]

    pows = alpha_rev**(np.arange(n+1))

    scale_arr = 1/pows[:-1]
    offset = chart_data_fl[0]*pows[1:]
    pw0 = alpha*alpha_rev**(n-1)

    mult = chart_data_fl*pw0*scale_arr
    cumsums = mult.cumsum()
    out = offset + cumsums*scale_arr[::-1]
    out_float = float(out[-1])
    return out_float

def ema_2(chart_data, period):
    alpha = 2/(period +1.0)
    alpha_rev = 1-alpha
    chart_data_fl = np.array(chart_data,dtype=float)
    n = chart_data_fl.shape[0]    

    pows = alpha_rev**(np.arange(n+1))
   
    scale_arr = 1/pows[:-1]
    offset = chart_data_fl[0]*pows[1:] 
    pw0 = alpha*alpha_rev**(n-1)

    mult = chart_data_fl*pw0*scale_arr
    cumsums = mult.cumsum()
    out = offset + cumsums*scale_arr[::-1]
    return out

if __name__ == "__main__":
    client = Poloniex(conf.api_key, conf.secret)

    tickers = client.returnTicker().keys()
    
    pairs = []

    now = datetime.datetime.now()

    balance = client.returnBalances()
    
    
    for ticker in tickers:
        if ticker.startswith('BTC'):
            pairs.append(ticker)

    for i in range(1, 2):
        print "%i/%i" % (now.day,now.month)
		
        for pair in pairs:             		
	    chart_data_organized = []
	    timestamp = time.time()
	    timestamp_range = timestamp - (900 * 288)	
    	    chart_data=client.returnChartData(pair, 900, timestamp_range, timestamp)
  	    #for k in range(1,len(chart_data)):
	     #   chart_data_organized.append(chart_data[k-1]['close'])
            lo_ema = ema(chart_data,5)
		
	    easy_pair = pair.split('_')[1]
            print "%s - %f" % (pair.split('_')[1],lo_ema)
