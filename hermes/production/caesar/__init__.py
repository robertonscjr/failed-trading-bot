from exchange.backtesting import Backtesting
from exchange.poloniex import Poloniex
from exchange.poloniex import PoloniexError
from strategy.chespirito import Chespirito
from strategy.hole import Hole
from utils import conf
import time
import os
 

class Caesar(object):
    def __init__(self, poloniex):
        self.running = {}
        self.balance_ratio = 3

        self.minimum = {}
        self.maximum = {}
	
	
        forbidden_pairs = ['BTC_ETH',  
                           'BTC_XRP', 'BTC_PINK', 'ETH_BCH',
                           'BTC_GAS', 'BTC_LSK', 'BTC_VIA',
			   'BTC_BTM', 'BTC_NMC']
        

        allowed_first_coins = ['BTC']

        ticker = poloniex.returnTicker()
        for pair in ticker:
            last = float(ticker[pair]['last'])
            first_candle = poloniex.returnChartData(pair, 900)[0]
            self.minimum[pair] = first_candle['open']
            self.maximum[pair] = first_candle['open']

        while(True):
            try:
                ticker = poloniex.returnTicker()
                all_orders = poloniex.returnOpenOrders('all')
                balances = poloniex.returnBalances()
		24_volume = poloniex.return24Volume()
            except PoloniexError as e:
                continue

            for pair in ticker:
                # Context variables
                last = float(ticker[pair]['last'])

                lowest_ask = float(ticker[pair]['lowestAsk'])
                highest_bid = float(ticker[pair]['highestBid'])
		24h_volume = float(24_volume[pair]['BTC'])
		base_volume = float(ticker[pair]['baseVolume'])

                first_coin = pair.split("_")[0]
                second_coin = pair.split("_")[1]

                first_balance = float(balances[first_coin])
                second_balance = float(balances[second_coin])

                open_orders = all_orders[pair] 

                # Strategy variables
                have_cases_enough = highest_bid * 100000 > 1.0
                have_hole = (bidask_ratio > conf.desired_hole)
                exist_open_orders = len(open_orders) > 0
                small_amount = second_balance * highest_bid <= 0.0001
                bidask_ratio = ((lowest_ask/highest_bid - 1) * 100)
		good_volume = (24h_volume > 20.0)
   		volume_spike = (base_volume>(24h_volume/288)) 
		
                # Thread variables
                is_running = pair in self.running
                forbidden_pair = pair in forbidden_pairs
                allowed_first_coin = first_coin in allowed_first_coins
         
                # Update running pairs
                self.update_running_pairs(pair)

                # If some coin gave error, fix it
                self.repair_running_pairs(pair)

                if last < self.minimum[pair] and second_balance == 0.0:
                    self.minimum_was_changed[pair] = False
                    self.minimum[pair] = last
                    continue

                ratio = last/self.minimum[pair] - 1.0
                can_enter_strategy = have_hole and have_cases_enough and good_volume \
                                         and (last >= self.minimum[pair] * 1.015)
 
                if not is_running and can_enter_strategy and \
                allowed_first_coin and not forbidden_pair:
                    print "%s: %.3f - %.3f" % (pair, last, self.minimum[pair])
#                   balance = (first_balance \
#                              / (self.balance_ratio - len(running)))
                    balance = (first_balance * conf.balance_percentage)
 
                    run = Hole(poloniex, pair, conf.desired_hole, 
                                     balance, False)
  
                    self.running[pair] = run
                    run.start()
                    
            time.sleep(5)

    def update_running_pairs(self, pair, is_running):
        if is_running and not self.running[pair].isAlive():
            del self.running[pair]

    def repair_running_pairs(self, pair):
        possible_error = (exist_open_orders or second_balance != 0.0)
        if not is_running and possible_error and have_cases_enough \
        and allowed_first_coin and not forbidden_pair:
            for order in open_orders:
                poloniex.cancelOrder(order['orderNumber'])

#           balance = (first_balance \
#                      / (self.balance_ratio - len(running)))
            balance = (first_balance * conf.balance_percentage)
            if second_balance != 0.0 and not small_amount:
                run = Hole(poloniex, pair, conf.desired_hole, 
                                  balance, True)
     
                self.running[pair] = run
                run.start()
                continue

    def _time(self):
        return time.asctime(time.localtime(time.time()))

 
if __name__ == "__main__":
    client = Poloniex(conf.api_key, conf.secret)
 
    try:
        caesar = Caesar(client)
    except KeyboardInterrupt:
        os._exit(1) 
