from exchange.poloniex import Poloniex
from utils import conf
import os
import time

if __name__ == "__main__":
    client = Poloniex(conf.api_key, conf.secret)
    ticker = client.returnTicker()

    total_btc = 0.0

    buy_btc = 0.0
    sell_btc = 0.0

    start_date = 1507698000
    end_date = 9999999999

    history = client.returnTradeHistory('all', start_date, end_date)

    for pair in history:
        if pair == 'BTC_ETH': 
            continue

        for trade in history[pair]:
            if trade['type'] == 'sell':
                sell_btc = sell_btc + float(trade['total'])
            if trade['type'] == 'buy':
                buy_btc = buy_btc + float(trade['total'])

    print "At %s BUY : %s" % (pair,buy_btc)
    print "SELL: %s" % sell_btc
    print "SELL-BUY: %s" % (sell_btc-buy_btc)
