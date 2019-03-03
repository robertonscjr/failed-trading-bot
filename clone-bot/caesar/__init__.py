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
        self.client = client
        self.running = {}

        while(True):
            try:
                ticker = self.client.returnTicker()
                all_orders = self.client.returnOpenOrders('all')
                balances = self.client.returnBalances()
            except PoloniexError:
                continue

            for pair in ticker:
                lowest_ask = float(ticker[pair]['lowestAsk'])
                highest_bid = float(ticker[pair]['highestBid'])
                bidask_ratio = ((lowest_ask/highest_bid - 1) * 100)

                have_hole = bidask_ratio > conf.desired_hole
                have_reverse_hole = highest_bid > lowest_ask

                have_cases_enough = highest_bid * 10000 > 1.0
                first_coin = pair.split("_")[0]
                second_coin = pair.split("_")[1]

                open_orders = all_orders[pair] 
                exist_open_orders = len(open_orders) > 0
                
                second_balance = float(balances[second_coin])

                forbidden_pairs = ['BTC_ETH', 'BTC_LTC', 'BTC_BCH', 
                                   'BTC_XRP', 'BTC_PINK', 'ETH_BCH',
                                   'BTC_GAS', 'BTC_LSK', 'BTC_VIA']

                allowed_first_coins = ['BTC']

                small_amount = second_balance * highest_bid <= 0.0001

                is_running = pair in self.running
                forbidden_pair = pair in forbidden_pairs
                allowed_first_coin = first_coin in allowed_first_coins
 
                possible_error = (exist_open_orders or second_balance != 0.0)

                # The pair's execution ended
                if is_running and not self.running[pair].isAlive():
                    del self.running[pair]

                # The pair probably gave error (Reverse hole test)
                if not is_running and possible_error and allowed_first_coin \
                and not forbidden_pair:
                    for order in open_orders:
                        self.client.cancelOrder(order['orderNumber'])

                    if second_balance != 0.0 and not small_amount:
                        run = ReverseHole(self.client, pair, 
                                          conf.balance_percentage, True)
     
                        self.running[pair] = run
                        run.start()
                        continue

                # The pair probably gave error (Hole test)
                if not is_running and possible_error and have_cases_enough \
                and allowed_first_coin and not forbidden_pair:
                    for order in open_orders:
                        self.client.cancelOrder(order['orderNumber'])

                    if second_balance != 0.0 and not small_amount:
                        run = Hole(self.client, pair, conf.desired_hole, 
                                          conf.balance_percentage, True)
     
                        self.running[pair] = run
                        run.start()
                        continue
                        
                can_enter_strategy = have_hole and have_cases_enough

 
                # Test conditions to enter in pair (Reverse Hole)
#               if have_reverse_hole and allowed_first_coin and 
#               not forbidden_pair:
#                   run = ReverseHole(self.client, pair, 
#                                     conf.balance_percentage, False)
#                   self.running[pair] = run
#                   run.start()

                # Test conditions to enter in pair (Hole)
                if not is_running and can_enter_strategy and \
                allowed_first_coin and not forbidden_pair:
                    run = Hole(self.client, pair, conf.desired_hole, 
                                     conf.balance_percentage, False)

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
