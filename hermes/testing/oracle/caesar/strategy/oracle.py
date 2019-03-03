from exchange.poloniex import Poloniex
from exchange.poloniex import PoloniexError
from utils import conf
import time
from threading import Thread
import traceback

class Oracle(Thread):
    def __init__(self, signal_data): 
        Thread.__init__(self)

        self.entry = signal_data['entry']
        self.target = signal_data['target']
        self.stop = signal_data['stop']
        self.exchange = signal_data['exchange']
        self.gr = signal_data['gr']

        self.buy_order = False
        self.sell_order = False
        self.bought = False
        self.sold = False

        self.end = False


    def run(self):
        print "(%s) - Enter in pair: %s" % (self.pair, self._time())
        while not self.end:
            try:
                self.update() 
                if not self.bought:
                    self.purchase()
                else:
                    self.sale()
            except PoloniexError as e:
                print "(%s) - Exception: %s : %s" % (self.pair, e, 
                                                     self._time())

                print traceback.print_exc()
                self.end = True

            time.sleep(1)

        print "(%s) - Leaving the pair: %s" % (self.pair, self._time())


    def purchase(self):
        balance = self.returnBalance()

        if not self.buy_order:
            self.buy_order = True
            self.buy(self.entry, balance)
            print "%s - Buy order placed at %.8f" % (self._time(), 
                                                     self.entry)


    # TODO
    def buy(self, price, amount):
        pass


    def sale(self):
        if self.sold():
            self.end = True
            return

        if self._highest_bid() <= self.stop:
            self.cancel_orders()
            self.sell(self._highest_bid)

            print "(%s) - Sell order placed to escape at %.8f" % \
                                                         (self._time(), 
                                                          self._highest_bid())

        if not self.sell_order:
            self.sell_order = True
            self.sell(self.target)
            print "%s - Sell order placed at %.8f" % (self._time(), 
                                                      self.target)


    # TODO
    def sell(self, price, amount):
        pass


    def update(self):
        self.trade_history = self.client.returnTradeHistory(self.pair)
        self.bought = self.was_bought()

 
    # TODO
    def bought(self):
        pass


    # TODO
    def sold(self):
        pass


    # TODO
    def _lowest_ask(self):
        pass 


    # TODO
    def _highest_bid(self):
        pass


    def _time(self):
        return time.asctime(time.localtime(time.time()))
