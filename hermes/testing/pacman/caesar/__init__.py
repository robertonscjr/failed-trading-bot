from exchange.backtesting import Backtesting
from exchange.poloniex import Poloniex
from exchange.poloniex import PoloniexError
from strategy.chespirito import Chespirito
from strategy.pacman import Pacman
from utils import conf
import time
import os
 

class Caesar(object):
    def __init__(self, client):
        self.client = client
        self.running = {}
        self.minimum = {}

        ticker = self.client.returnTicker()
        for pair in ticker:
            candlestick = self.client.returnChartData(pair, 900)
            self.minimum[pair] = float(candlestick[0]['open'])

        while(True):
            try:
                ticker = self.client.returnTicker()
                all_orders = self.client.returnOpenOrders('all')
                balances = self.client.returnBalances()
            except PoloniexError:
                continue

            for pair in ticker:
                first_coin = pair.split("_")[0]
                highest_bid = float(ticker[pair]['highestBid'])
                have_cases_enough = highest_bid * 10000 > 1.0
                if not (first_coin == 'BTC' and have_cases_enough):
                    continue

                open_orders = all_orders[pair] 
                exist_open_orders = len(open_orders) > 0
                second_coin = pair.split("_")[1]
                second_balance = float(balances[second_coin])

                is_running = pair in self.running
                if is_running and not self.running[pair].isAlive():
                    del self.running[pair]

                is_running = pair in self.running
                if is_running:
                    continue

                possible_error = (exist_open_orders or second_balance != 0.0)
                small_amount = second_balance * highest_bid <= 0.0001
                if not is_running and possible_error:
                    for order in open_orders:
                        self.client.cancelOrder(order['orderNumber'])
 
                    if second_balance != 0.0 and not small_amount:
                        run = Pacman(self.client, pair, 
                                   conf.balance_percentage, 
                                   self.minimum[pair], True)
     
                        self.running[pair] = run
                        run.start()
                        continue

                last = float(ticker[pair]['last'])
                if last < self.minimum[pair]:
                    self.minimum[pair] = last
                    continue

                ratio = last/self.minimum[pair] - 1.0
                if ratio >= 5.0:
                    print "%s: %.3f" % (pair, ratio * 100)

                if not is_running and last >= self.minimum[pair] * 1.05:
                    candlestick = self.client.returnChartData(pair, 300)
                    last_candle = candlestick[len(candlestick)-1]
                    penult_candle = candlestick[len(candlestick)-2]
                    green_candle = (last_candle['close'] > last_candle['open'] \
                        and penult_candle['close'] > penult_candle['open'])

                    if green_candle:
                        run = Pacman(self.client, pair, 
                                     conf.balance_percentage, 
                                     self.minimum[pair], False)

                        self.running[pair] = run
                        run.start()
                    
            time.sleep(5)

    def _time(self):
        return time.asctime(time.localtime(time.time()))

 
if __name__ == "__main__":
    client = Poloniex(conf.api_key, conf.secret)
 
    try:
        caesar = Caesar(client)
    except KeyboardInterrupt:
        os._exit(1) 
