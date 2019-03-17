from poloniex import Poloniex
from poloniex import PoloniexError
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
                self.caesar_log.log("(%s) - Exception: %s : %s" % (self.pair, e, 
                                                     self._time()))

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

        amount = float(0.00011 / float(buy_price))

        self.client.buy(self.pair,
                        buy_price,
                        amount, 
                        'fillOrKill')['orderNumber']

        self.caesar_log.log("(%s) - Buy order executed at %.8f : %s" % (self.pair, 
                                                          buy_price,
                                                          self._time()))

	self.bought = True

    def sale_action(self):
        ticker = poloniex.get_ticker(self.client)
        highest_bid = poloniex.highest_bid(ticker, self.pair)
      # candle_open, candle_close = poloniex.candle_info(self.client,
      #                                                  self.pair)

      # candle_ratio = (candle_open / candle_close - 1.0) * 100.0
#       candle_ratio = (candle_open / poloniex.last(ticker, self.pair) - 1.0) * 100.0
        lo_threshold = self.buy_price * (1 - 0.5)

        chart_data = self.client.returnChartData(self.pair, 300)
#       lo_ma = poloniex.ema(chart_data, 7)
#       hi_ma = poloniex.ema(chart_data, 21)
        ma_1 = poloniex.ema(chart_data, 3)
        ma_2 = poloniex.sma(chart_data, 7)
        ma_3 = poloniex.ema(chart_data, 21)

        ma = (ma_3 > ma_2 and ma_3 > ma_1)
 
#	if candle_ratio >= 2.0 or highest_bid <= lo_threshold:
           #print "(%s) - Candle ratio: %.2f / Highest bid: %.8f : %s" % \
           #                                                (self.pair,
           #                                                 candle_ratio, 
           #                                                 highest_bid, 
           #                                                 self._time())

 	if ma or highest_bid <= lo_threshold:
            self.caesar_log.log("(%s) - Highest bid: %.8f / Buy price: %.8f : %s" % \
                                                               (self.pair,
                                                                highest_bid, 
                                                                self.buy_price,
                                                                self._time()))

            self.caesar_log.log("(%s) - EMA(3): %.8f / EMA(7): %.8f / EMA(21): %.8f : %s" % \
                                              (self.pair,
                                               ma_1, 
                                               ma_2, 
                                               ma_3,
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
