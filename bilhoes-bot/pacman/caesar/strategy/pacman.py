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
        self.buy_amount = 0.0
        self.end = False

        if bought:
            self.buy_price = self._last_buy_price()
            self.buy_amount = self._last_all_buy_amount()

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
        lowest_ask = poloniex.lowest_ask(ticker, self.pair)
        order_book = poloniex.get_order_book(self.client)

        attempts = 0
        second_balance = self.balance
        while second_balance >= 0.0001:
            self.caesar_log.log("(%s) - Executing buy order at %.8f with %.5f of amount (Attempt %d) : %s" % \
                                              (self.pair,
                                               lowest_ask,
                                               second_balance,
                                               attempts,
                                               self._time()))

            try:
                order_type = 'immediateOrCancel'
                amount = float(second_balance / float(lowest_ask))
                self.client.buy(self.pair, lowest_ask, amount, order_type)
                second_balance = second_balance - self._last_buy_amount() * float(lowest_ask)

            except PoloniexError as e:
                attempts = attempts + 1
                order_book = poloniex.get_order_book(self.client)
                lowest_ask = poloniex.get_first_order_price(order_book, 
                                                             self.pair, 
                                                             'asks')

        self.buy_price = lowest_ask
        self.caesar_log.log("(%s) - Buy order executed at %.8f : %s" % (self.pair, 
                                                                        lowest_ask,
                                                                        self._time()))

	self.bought = True

    def sale_action(self):
        ticker = poloniex.get_ticker(self.client)
        highest_bid = poloniex.highest_bid(ticker, self.pair)

        timestamp = time.time()
        timestamp_range = timestamp - (900 * 320)
        chart_data = self.client.returnChartData(self.pair, 900, timestamp_range, timestamp)

        data = [float(chart['close']) for chart in chart_data[:len(chart_data)-1]]
        ma_1 = poloniex.ema(data, 16)
        ma_2 = poloniex.sma(data, 52)
        ma_3 = poloniex.ema(data, 42)

        last_close = float(chart_data[len(chart_data)-2]['close'])
        ma = (ma_1 < ma_2 and ma_1 < ma_3)

        sell_signal = (ma and last_close < ma_2) 
 	if sell_signal:
            self.caesar_log.log("(%s) - EMA(16): %.8f / SMA(52): %.8f / EMA(42): %.8f : %s" % \
                                              (self.pair,
                                               ma_1, 
                                               ma_2, 
                                               ma_3,
                                               self._time()))

            attempts = 0
            while True:
                self.caesar_log.log("(%s) - Executing sell order at %.8f (Attempt %d) : %s" % \
                                                  (self.pair,
                                                   highest_bid,
                                                   attempts,
                                                   self._time()))

                try:
                    balances = poloniex.get_balances(self.client)
                    second_balance = poloniex.get_balance(balances, self.second_coin)
                    if second_balance < 0.0001:
                        break
                    order_type = 'immediateOrCancel'
                    self.client.sell(self.pair, highest_bid, second_balance, order_type)
                    

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

    def _last_buy_amount(self):
        trade_history = self.client.returnTradeHistory(self.pair,
                                                       1507842000,
                                                       9999999999)

        for trade in trade_history:
            if trade['type'] == 'buy':
                return float(trade_history[0]['amount'])

    def _last_all_buy_amount(self):
        trade_history = self.client.returnTradeHistory(self.pair,
                                                       1507842000,
                                                       9999999999)
        amount = 0.0

        for i in range(len(trade_history)-1):
            if trade_history[i]['type'] == 'buy' and trade_history[i + 1]['type'] == 'buy':
                amount = amount + float(trade_history[i]['amount'])

            if trade_history[i]['type'] == 'buy' and trade_history[i + 1]['type'] == 'sell':
                amount = amount + float(trade_history[i]['amount'])
                return amount

    def _last_all_sell_amount(self):
        trade_history = self.client.returnTradeHistory(self.pair,
                                                       1507842000,
                                                       9999999999)
        amount = 0.0
        for i in range(len(trade_history)-1):
            if trade_history[i]['type'] == 'sell' and trade_history[i + 1]['type'] == 'sell':
                amount = amount + float(trade_history[i]['amount'])

            if trade_history[i]['type'] == 'sell' and trade_history[i + 1]['type'] == 'buy':
                amount = amount + float(trade_history[i]['amount'])
                return amount

    def _last_sell_amount(self):
        trade_history = self.client.returnTradeHistory(self.pair,
                                                       1507842000,
                                                       9999999999)

        for trade in trade_history:
            if trade['type'] == 'sell':
                return float(trade_history[0]['amount'])
