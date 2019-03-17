from poloniex import Poloniex
from poloniex import PoloniexError
from utils import conf
from utils import poloniex
import utils
import time
from threading import Thread
import traceback

class Chatuba(Thread):
    def __init__(self, client, pair, balance, bought):
        Thread.__init__(self)
        self.client = client
        self.pair = pair
        self.first_coin = pair.split("_")[0]
        self.second_coin = pair.split("_")[1]
        self.balance = balance
        self.bought = bought
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
                print "(%s) - Exception: %s : %s" % (self.pair, e, 
                                                     self._time())

                self.end = True

        print "(%s) - Leaving the pair: %s" % (self.pair, self._time())

    def purchase_action(self):
        ticker = poloniex.get_ticker(self.client)
        order_book = poloniex.get_order_book(self.client)

        buy_price = poloniex.get_first_order_price(order_book, 
                                                   self.pair, 
                                                   'asks')
        self.buy_price = buy_price

        amount = float(0.00011 / float(buy_price))

        self.client.buy(self.pair,
				buy_price,
                        amount, 
                        'fillOrKill')['orderNumber']

        print "(%s) - Buy order executed at %.8f : %s" % (self.pair, 
                                                          buy_price,
                                                          self._time())

	self.bought = True

    def sale_action(self):
        ticker = poloniex.get_ticker(self.client)
        highest_bid = poloniex.highest_bid(ticker, self.pair)

        chart_data = client.returnChartData(pair, 900)
        lo_ma = poloniex.sma(chart_data, 100)
        hi_ma = poloniex.sma(chart_data, 200)
        can_exit = (highest_bid > lo_ma) #Talvez o close do candle? 

 	if can_exit:
            print "(%s) - Low MA: %.8f / High MA: 0.8f : %s" % \
                                                            (self.pair,
                                                             lo_ma, 
                                                             hi_ma, 
                                                             self._time())

            balances = self.client.returnBalances()
            second_balance = balances[self.second_coin]

            while True:
                try:
                    order_type = 'fillOrKill'
                    self.client.sell(self.pair, highest_bid, second_balance, order_type)
                    break

                except PoloniexError as e:
                    ticker = poloniex.get_ticker(self.client)
                    highest_bid = poloniex.highest_bid(ticker, self.pair)

            print "(%s) - Sell order executed at %.8f : %s" % \
                                                            (self.pair, 
                                                             sell_price, 
                                                             self._time())
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
