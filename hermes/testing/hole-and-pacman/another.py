from exchange.poloniex import Poloniex
from utils import conf
import os
import time
import datetime

if __name__ == "__main__":
    client = Poloniex(conf.api_key, conf.secret)
 
    today_hist = client.returnTradeHistory('all')
  
    s = '2017-10-31 00:00:00'
  
    start = int(time.mktime(time.strptime(s, '%Y-%m-%d %H:%M:%S'))) - 3600 * 3
    end = start + 86399
    end = start - 86399 * 65
    today_hist = client.returnTradeHistory('all', start, end)
    today_hist = client.returnTradeHistory('all', end, start)
  
    differences = {}
  
    for pair in today_hist:
        count = 0.0
  
        if today_hist[pair][0]['type'] == 'buy':
            for history in today_hist[pair]:
                if history['type'] == 'sell':
                    break
                count = count + float(history['total'])
  
        if today_hist[pair][len(today_hist[pair])-1]['type'] == 'sell':
            found = False
            refvalue = start
            while not found:
                today = client.returnTradeHistory(pair, 
                              refvalue - 86400 * 30, refvalue)
  
                for history in today:
                    if history['type'] == 'buy':
                        count = count - float(history['total'])
                        found = True
                        break
  
                refvalue = refvalue - 86400 * 30
  
        for history in today_hist[pair]:
            if history['type'] == 'sell':
                total = float(history['total']) * (1.0 - float(history['fee']))
                count = count + total
        
            else:
    		count = count - float(history['total'])
  
        differences[pair] = count
        if count != 0.0:
            print "%s - %.8f" % (pair.split('_')[1], count)
  
         
    total = 0.0
  
    for value in differences.values():
        total = total + value
  
    print "TOTAL: %.8f" % total
  
