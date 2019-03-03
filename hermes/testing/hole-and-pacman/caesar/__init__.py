from exchange.backtesting import Backtesting
from exchange.poloniex import Poloniex
from exchange.poloniex import PoloniexError
from strategy.chespirito import Chespirito
from strategy.hole import Hole
from utils import conf
import time
import os
 

class Caesar(object):
    def __init__(self, client):
        # Here is my code, come on to you understand everything
        f = open("logs/hole.log","w")

        self.client = client
        self.running = {}
        self.minimum_was_changed = {}
        self.balance_ratio = 3

        # PACMAN init
        self.minimum = {}
        ticker = self.client.returnTicker()
        for pair in ticker:
            last = float(ticker[pair]['last'])
            self.minimum[pair] = last
            self.minimum_was_changed[pair] = False


        while(True):
            try:
                ticker = self.client.returnTicker()
                all_orders = self.client.returnOpenOrders('all')
                balances = self.client.returnBalances()
                volume_diario = self.client.return24hVolume()
            except PoloniexError as e:
#               print "Exception in core: %s : %s" % (e, self._time())
                continue

            for pair in ticker:
		first_coin = pair.split("_")[0]
                second_coin = pair.split("_")[1]
                
		last = float(ticker[pair]['last'])
                lowest_ask = float(ticker[pair]['lowestAsk'])
                highest_bid = float(ticker[pair]['highestBid'])
                bidask_ratio = ((lowest_ask/highest_bid - 1) * 100)
		
		change = float(ticker[pair]['percentChange'])	
		volume_do_dia = float(volume_diario[pair][first_coin])
		base_volume = float(ticker[pair]['baseVolume'])

                have_hole = (bidask_ratio > conf.desired_hole)
                have_cases_enough = highest_bid * 100000 > 1.0
               
		good_volume = (volume_do_dia > 50.0)
   		volume_spike = (base_volume>(volume_do_dia/288)) 
                
		open_orders = all_orders[pair] 
                exist_open_orders = len(open_orders) > 0
                
                first_balance = float(balances[first_coin])
                second_balance = float(balances[second_coin])

                forbidden_pairs = ['BTC_ETH', 'BTC_BCH', 'BTC_LTC',
                                   'BTC_XRP', 'BTC_PINK', 'ETH_BCH',
				   'BTC_FLO', 'BTC_BLK', 'BTC_HUC',
				   'BTC_EXP', 'BTC_GAS']

                allowed_first_coins = ['BTC']

                small_amount = second_balance * highest_bid <= 0.0001

                is_running = pair in self.running
                forbidden_pair = pair in forbidden_pairs
                allowed_first_coin = first_coin in allowed_first_coins
 
                possible_error = (exist_open_orders or second_balance != 0.0)
         
                if second_balance != 0.0 and not self.minimum_was_changed[pair]:

                    self.minimum[pair] = last
                    self.minimum_was_changed[pair] = True

                # The pair's execution ended
                if is_running and not self.running[pair].isAlive():
                    print "(%s) - Remove ended execution of this pair: %s" % (pair, self._time())
                    self.minimum[pair] = last
                    del self.running[pair]
 
                # The pair probably gave error (Hole test)
                if not is_running and possible_error and have_cases_enough \
                and allowed_first_coin and not forbidden_pair:
                    for order in open_orders:
                        print "(%s) - Cancel orders of pair in error: %s" % (pair, self._time())
                        self.client.cancelOrder(order['orderNumber'])

#                   balance = (first_balance \
#                              / (self.balance_ratio - len(self.running)))
                    balance = (first_balance * conf.balance_percentage)
                    if second_balance != 0.0 and not small_amount:
                        print "(%s) - Enter in pair with error: %s" % (pair, self._time())
                        run = Hole(self.client, pair, conf.desired_hole, 
                                          balance, True)
     
                        self.running[pair] = run
                        run.start()
                        continue

                if last < self.minimum[pair] and second_balance == 0.0:
#                   print "(%s) - Update minimum: %s" % (pair, self._time())
                    self.minimum_was_changed[pair] = False
                    self.minimum[pair] = last
                    continue

                ratio = last/self.minimum[pair] - 1.0
                
		timestamp       = time.time()
		timestamp_range = timestamp - (300 * 5)
                candle = self.client.returnChartData(pair, 300, timestamp_range, timestamp)
                
		can_enter_strategy = (False and have_hole and have_cases_enough )
                #can_enter_strategy = (have_hole and have_cases_enough and good_volume and have_green and green_change )
 
                if not is_running and can_enter_strategy and \
                allowed_first_coin and not forbidden_pair:
                    print "(%s) - Entering in pair: %s" % (pair, self._time())
#                   balance = (first_balance \
#                              / (self.balance_ratio - len(self.running)))
                    balance = (first_balance * conf.balance_percentage)
 
                    run = Hole(self.client, pair, conf.desired_hole, 
                                     balance, False)
  
                    self.running[pair] = run
                    run.start()
                    
            time.sleep(5)

    def _time(self):
        return time.asctime(time.localtime(time.time()))

         
    def candle_size(self,candle): 
        open_candle = float(candle['open'])
        close_candle = float(candle['close'])
	
        return ((close_candle / open_candle)-1.0) * 100
    
    def candle_gigante(self,candle):
	try:
            first_candle = self.candle_size(candle[len(candle)  -2])
            second_candle = self.candle_size(candle[len(candle) -3])
	except:
	    return False
        if (first_candle > 0) and (second_candle < 0) \
            and (first_candle > (2 * abs(second_candle) )):

	    return True       
    
    def candle_green(self,candle):
	try:
            first_candle = self.candle_size(candle[len(candle)  -1])
            second_candle = self.candle_size(candle[len(candle) -2])
	except:
	    return False
        if first_candle > -4:

	    return True       

if __name__ == "__main__":
    client = Poloniex(conf.api_key, conf.secret)
 
    try:
        caesar = Caesar(client)
    except KeyboardInterrupt:
        os._exit(1) 
