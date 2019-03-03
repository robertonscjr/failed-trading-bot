from exchange.poloniex import Poloniex
from exchange.poloniex import PoloniexError
from utils import conf
from utils import poloniex
import utils
import time
from threading import Thread
import traceback

class Pacman(Thread):
    def __init__(self, client, pair, balance, bought, caesar_log):
        Thread.__init__(self)
        self.client = client
        self.pair = pair
        self.first_coin = pair.split("_")[0]
        self.second_coin = pair.split("_")[1]
        self.balance = balance
        self.bought = bought
        self.caesar_log = caesar_log
        self.buy_price = 0.0
        self.end = False

        if bought:
            self.buy_price = self._last_buy_price()

    def run(self):
        while not self.end:
            try:
                if not self.bought:
                    self.purchase_action()
                else:
                    self.sale_action()

            except PoloniexError as e:
                self.end = True

        self.caesar_log.log("(%s) - Leaving the pair: %s" % (self.pair, self._time()))

    def purchase_action(self):
        ticker = poloniex.get_ticker(self.client)
        order_book = poloniex.get_order_book(self.client)

        buy_price = poloniex.get_first_order_price(order_book, 
                                                   self.pair, 
                                                   'asks')
        self.buy_price = buy_price

#       order_amount = float(poloniex.get_first_order_amount(order_book,
#                                                      self.pair,
#                                                      'asks'))
#
#       my_amount = float(float(self.balance) / float(buy_price))
#
#       if float(my_amount) <= float(order_amount):
#           amount = float(my_amount)
#       else:
#           amount = float(order_amount)

        amount = float(float(self.balance) / float(buy_price))

        self.client.buy(self.pair,
                        buy_price,
                        amount, 
                        'immediateOrCancel')['orderNumber']
 
        self.caesar_log.log("(%s) - Buy order executed at %.8f : %s" % (self.pair, 
                                                          buy_price,
                                                          self._time()))

	self.bought = True

    def sale_action(self):
        ticker = poloniex.get_ticker(self.client)
        highest_bid = poloniex.highest_bid(ticker, self.pair)
        last = poloniex.last(ticker, self.pair)
#       lo_threshold = self.buy_price * (1 - 0.05)
       #hi_threshold = self.buy_price * (1 + 0.03)

        timestamp = time.time()
        timestamp_range = timestamp - (900 * 320)
        chart_data = self.client.returnChartData(self.pair, 900, timestamp_range, timestamp)
        chart_data = chart_data[:len(chart_data)-1]

        lo_ma = poloniex.ema(chart_data, 50 * 2)
        hi_ma = poloniex.ema(chart_data, 100 * 2)

        last_close = float(chart_data[len(chart_data)-2]['close'])
 	if (last_close > lo_ma):
            stop = False # highest_bid <= lo_threshold or highest_bid >= hi_threshold


            self.caesar_log.log("(%s) - Highest bid: %.8f / Buy price: %.8f : %s" % \
                                                               (self.pair,
                                                                highest_bid, 
                                                                self.buy_price,
                                                                self._time()))

            self.caesar_log.log("(%s) - LOW: %.8f / HIGH: %.8f: %s" % \
                                              (self.pair,
                                               lo_ma, 
                                               hi_ma, 
                                               self._time()))


            attempts = 0
            second_balance = -1.0
            while second_balance is not 0.0:
                if attempts is 20:
                    return

                self.caesar_log.log("(%s) - Executing sell order at %.8f (Attempt %d) : %s" % \
                                                  (self.pair,
                                                   highest_bid,
                                                   attempts,
                                                   self._time()))

                try:
                    balances = self.client.returnBalances()
                    second_balance = float(balances[self.second_coin])
                    order_type = 'fillOrKill'
                    self.client.sell(self.pair, highest_bid, second_balance, order_type)
                    break

                except PoloniexError as e:
                    attempts = attempts + 1
                    order_book = poloniex.get_order_book(self.client)
                    highest_bid = poloniex.get_first_order_price(order_book, 
                                                                 self.pair, 
                                                                 'bids')

            self.caesar_log.log("(%s) - Sell order executed at %.8f : %s" % \
                                                            (self.pair, 
                                                             highest_bid, 
                                                             self._time()))
            self.end = True

    def _time(self):
        return time.asctime(time.localtime(time.time()))

    def _last_buy_price(self):
        trade_history = self.client.returnTradeHistory(self.pair,
                                                       1507842000,
                                                       9999999999)

        for trade in trade_history:
            if trade['type'] == 'buy':
                return float(trade_history[0]['rate'])
