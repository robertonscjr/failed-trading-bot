from exchange.poloniex import Poloniex
from exchange.poloniex import PoloniexError
from utils import conf
import time
from threading import Thread
import traceback

class Pacman(Thread):
    """ Pacman Strategy.
    """

    def __init__(self, client, pair, balance_percentage, minimum, update):
        """ Constructor of Hole class """
        Thread.__init__(self)
        self.client = client

        self.pair = pair
        self.first_coin = self.pair.split("_")[0]
        self.second_coin = self.pair.split("_")[1]

        self.balance_percentage = balance_percentage
        self.minimum = minimum

        self.last_buy_order = None
        self.last_sell_order = None

        self.buy_id = None
        self.sell_id = None
 
        self.buy_order = False
        self.sell_order = False

        self.bought = False
        self.bought_verified = False
        self.sold = False

        self.buy_price = 0.0
        self.sell_price = None

        self.end = False
        self.first_exec = False

        self.updated = update

        if self.updated:
            self.buy_order       = True
            self.sell_order      = False
            self.bought          = True
            self.bought_verified = True
            self.sold            = False
            self.buy_price       = self.last_buy_price()
            self.sell_price      = self.check_price_to_sell()


    def last_buy_price(self):
        trade_history = self.client.returnTradeHistory(self.pair, 1507842000, 
                                                                  9999999999)

        for trade in trade_history:
            if trade['type'] == 'buy':
                return float(trade_history[0]['rate'])

        return 0.0


    def run(self):
        print "(%s) - Enter in pair: %s" % (self.pair, self._time())
        while not self.end:
            try:
                self.update() 
                if not self.bought:
                    self.purchase_action()
                else:
                    self.sale_action()
            except PoloniexError as e:
                print "(%s) - Exception: %s : %s" % (self.pair, e, 
                                                     self._time())

#               print traceback.print_exc()
                self.end = True

            time.sleep(conf.check_period)

        print "(%s) - Leaving the pair: %s" % (self.pair, self._time())


    def exists_open_orders(self, pair):
        self.open_orders = self.client.returnOpenOrders(self.pair)
        return len(self.client.returnOpenOrders(self.pair)) > 0
         

    def purchase_action(self):
        """ Constructor of Hole class
           
        Description about constructor.

        Args:
            x
        Returns:
            y
        Raises:
            z
        """
        balances = self.client.returnBalances()
        self.first_balance = float(balances[self.first_coin])
        self.ticker = self.client.returnTicker()[self.pair]

        last = float(self.ticker['last'])
        if last < self.minimum:
            self.minimum = last
            return

        if last >= self.minimum * 1.05:
            candlestick = self.client.returnChartData(self.pair, 300)
            last_candle = candlestick[len(candlestick)-1]
            penult_candle = candlestick[len(candlestick)-2]
            green_candle = (last_candle['close'] > last_candle['open'] \
                     and penult_candle['close'] > penult_candle['open'])

            if not green_candle:
                self.end = True
                return
        else:
            self.end = True
            return

        if not self.buy_order:
            self.buy_order = True
            self.buy()
            print "(%s) - Buy order placed at %.8f : %s" % (self.pair, 
                                                       self.buy_price,
                                                         self._time())

        else:
            self.order_book = self.client.returnOrderBook(self.pair, 2)
            self.last_buy_order = float(self.order_book['bids'][0][0])

            if self.buy_price < self.last_buy_order:
                self.client.cancelOrder(self.buy_id)
                self.buy()
                print "(%s) - Last buy order updated at %.8f : %s" % \
                                                           (self.pair,
                                                       self.buy_price,  
                                                         self._time())


    def buy(self):
        self.buy_price = self.check_price_to_buy() + 0.00000001
        amount = ((self.balance_percentage * self.first_balance)
                                               / self.buy_price)
  
        if amount * self.buy_price <= 0.0001:
            amount = 0.00011000 / self.buy_price
                     
        self.buy_id = str(self.client.buy(self.pair, 
                                          self.buy_price, 
                                          amount)['orderNumber'])
    

    def sale_action(self):
        """ Constructor of Hole class
           
        Description about constructor.

        Args:
            x
        Returns:
            y
        Raises:
            z
        """
        self.ticker = self.client.returnTicker()[self.pair]

        lo_threshold = self.buy_price * (1.0 - 0.05)

        self.sold = self.was_sold()
        if self.sold:
            self.last_buy_order = None
            self.last_sell_order = None
     
            self.buy_id = None
            self.sell_id = None
     
            self.buy_order = False
            self.sell_order = False
     
            self.bought = False
            self.bought_verified = False
            self.sold = False
     
            self.buy_price = 0.0
            self.sell_price = None
     
            self.end = False
            self.first_exec = False
            self.updated = False

            return

        if self._highest_bid() <= lo_threshold:
            if self.sell_order:
                self.client.cancelOrder(self.sell_id)

            self.sell_price = self._highest_bid()
            self.sell(self.sell_price)

            print "(%s) - Sell order placed to escape at %.8f : %s" % \
                                                            (self.pair, 
                                                       self.sell_price, 
                                                          self._time())
            self.end = True

        else:
            if not self.sell_order:
                self.sell_price = self.buy_price * (1 + 0.015)
                self.sell(self.sell_price)
                
                print "(%s) - Sell order placed at %.8f : %s" % \
                                                      (self.pair, 
                                                 self.sell_price, 
                                                    self._time())
                

    def exist_difference(self):
        number_of_orders = 5
        self.order_book = self.client.returnOrderBook(self.pair, 
                                                      number_of_orders)
        sell_orders = self.order_book['asks']
        value_orders = []

        for order in sell_orders:
            value_orders.append(float(order[0]))

        if value_orders[0] == self.sell_price:
            return True

        for i in range(number_of_orders - 1):
            if value_orders[i + 1] == self.sell_price:
                if value_orders[i + 1] - value_orders[i] > 0.00000100:
                    print "Exist difference %s" % self.pair
                    return True

        print "No exists difference %s" % self.pair
        return False


    def check_price_to_buy(self):
        number_of_orders = 2
        self.order_book = self.client.returnOrderBook(self.pair, 
                                                      number_of_orders)
        buy_orders = self.order_book['bids']
        value_orders = []

        for order in buy_orders:
            value_orders.append(float(order[0]))

        price_to_buy = value_orders[0]

        for i in range(number_of_orders - 1):
            if value_orders[i + 1] - value_orders[i] > 0.00000100:
                price_to_buy = value_orders[i+1] + 0.00000001

        return price_to_buy


    def check_price_to_sell(self):
        number_of_orders = 5
        self.order_book = self.client.returnOrderBook(self.pair, 
                                                      number_of_orders)
        sell_orders = self.order_book['asks']
        value_orders = []

        for order in sell_orders:
            value_orders.append(float(order[0]))

        price_to_sell = value_orders[0]

        for i in range(number_of_orders - 1):
            if value_orders[i + 1] - value_orders[i] > 0.00000100:
                price_to_sell = value_orders[i+1] - 0.00000001

        return price_to_sell


    def sell(self, sell_price):
        balances = self.client.returnBalances()
        self.second_balance = float(balances[self.second_coin])
        self.sell_price = sell_price 
        self.sell_id = str(self.client.sell(self.pair,
                                            self.sell_price, 
                                            self.second_balance)
                                            ['orderNumber'])
        self.sell_order = True


    def update(self):
        """ Constructor of Hole class
           
        Description about constructor.

        Args:
            x
        Returns:
            y
        Raises:
            z
        """
        self.trade_history = self.client.returnTradeHistory(self.pair)
        self.bought = self.was_bought()


    def was_bought(self):
        if not self.buy_order:
            return False

        if self.bought_verified:
            return True

        for history in self.trade_history:
            if history['orderNumber'] == self.buy_id \
            and not self.bought_verified:
                print "(%s) - Buy order executed : %s" % (self.pair, 
                                                      self._time())
                self.bought_verified = True

                return True

        return False


    def was_sold(self):
        if not self.sell_order:
            return False

        for history in self.trade_history:
            if history['orderNumber'] == self.sell_id:
                print "(%s) - Sell order executed : %s" % (self.pair, 
                                                       self._time())
                return True

        return False


    def _lowest_ask(self):
        return float(self.ticker['lowestAsk'])


    def _highest_bid(self):
        return float(self.ticker['highestBid'])


    def _time(self):
        return time.asctime(time.localtime(time.time()))
