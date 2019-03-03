from exchange.poloniex import Poloniex
from utils import conf
import os
import time
import datetime

def get_day_profit(pair, today, start, end, client):
    today_hist = {}
    today_hist[pair] = today

    differences = {}

    count = 0.0

    if today_hist[pair][0]['type'] == 'buy':
        for history in today_hist[pair]:
            if history['type'] == 'sell':
                break
            count = count + float(history['total'])

    # ate aqui de boa

    if today_hist[pair][len(today_hist[pair])-1]['type'] == 'sell':
        found = False
        refvalue = start
        while not found:
            today = client.returnTradeHistory(pair, 
                          refvalue - 86400, refvalue)

            for history in today:
                if history['type'] == 'buy':
                    count = count - float(history['total'])
                    found = True
                elif history['type'] == 'sell' and not found:
                    total = float(history['total']) * (1.0 - 
                                                       float(history['fee']))
                    count = count + total
                elif history['type'] == 'sell' and found:
                    break

            refvalue = refvalue - 86400

    for history in today_hist[pair]:
        if history['type'] == 'sell':
            total = float(history['total']) * (1.0 - float(history['fee']))
            count = count + total
    
        else:
            count = count - float(history['total'])

    return count
    

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

        if i > 21: start_date = '2018-%i-0%i 00:00:00' % (now.month,now.day)
        else: start_date = '2018-%i-%i 00:00:00' % (now.month,now.day)

        start = int(time.mktime(time.strptime(start_date, '%Y-%m-%d %H:%M:%S'))) - 3600 * 3

        end = start + 86399
       
        today_hist = client.returnTradeHistory('all', start, end)
        profits = []

        for pair in pairs:
            if pair not in today_hist:
                continue

            day_coin_profit = get_day_profit(pair, today_hist[pair], start, end, client)
            profits.append(day_coin_profit)
	    easy_pair = pair.split('_')[1]
            if day_coin_profit != 0.0:
                print "(%s)  -   %.8f" % (pair.split('_')[1], day_coin_profit)
	        
        print "TOTAL: %.8f" % sum(profits)
        print ""
	print (balance['BTC'])	
#   today_hist = client.returnTradeHistory('all')
#
#   import pdb; pdb.set_trace()
#
#   s = '2017-10-21 00:00:00'
#
#   start = int(time.mktime(time.strptime(s, '%Y-%m-%d %H:%M:%S'))) - 3600 * 3
#   end = start + 86399
#   end = start - 86399 * 65
#   today_hist = client.returnTradeHistory('all', start, end)
#   today_hist = client.returnTradeHistory('all', end, start)
#
#   differences = {}
#
#   for pair in today_hist:
#       count = 0.0
#
#       if today_hist[pair][0]['type'] == 'buy':
#           for history in today_hist[pair]:
#               if history['type'] == 'sell':
#                   break
#               count = count + float(history['total'])
#
#       if today_hist[pair][len(today_hist[pair])-1]['type'] == 'sell':
#           found = False
#           refvalue = start
#           while not found:
#               today = client.returnTradeHistory(pair, 
#                             refvalue - 86400 * 30, refvalue)
#
#               for history in today:
#                   if history['type'] == 'buy':
#                       count = count - float(history['total'])
#                       found = True
#                       break
#
#               refvalue = refvalue - 86400 * 30
#
#       for history in today_hist[pair]:
#           if history['type'] == 'sell':
#               total = float(history['total']) * (1.0 - float(history['fee']))
#               count = count + total
#       
#           else:
#   		count = count - float(history['total'])
#
#       differences[pair] = count
#       if count != 0.0:
#           print "%s - %.8f" % (pair.split('_')[1], count)
#
#        
#   total = 0.0
#
#   for value in differences.values():
#       total = total + value
#
#   print "TOTAL: %.8f" % total
#
