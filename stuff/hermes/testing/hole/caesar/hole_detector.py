from exchange.poloniex import Poloniex
from utils import conf
import os
import time

if __name__ == "__main__":
    client = Poloniex(conf.api_key, conf.secret)

    while(True):
        ticker = client.returnTicker()
     
        variation = {}
        for pair in ticker:
            lowest_ask = float(ticker[pair]['lowestAsk'])
            highest_bid = float(ticker[pair]['highestBid'])
            five_cases = highest_bid * 10000 > 1.0

            variation[pair] = ((lowest_ask/highest_bid - 1) * 100)
            if five_cases:
                variation[pair] = ((lowest_ask/highest_bid - 1) * 100)
     
        ordened_var = sorted(variation.items(), key=lambda x:x[1])
     
        for pair, value in reversed(ordened_var):
            first_coin = pair.split("_")[0]
            if value < 1.0 and first_coin == 'BTC':
                print "%9s - var: %.3f" % (pair, value)

        time.sleep(5)
