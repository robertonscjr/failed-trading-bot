from poloniex import Poloniex
from poloniex import PoloniexError
from strategy.pacman import Chatuba
from utils import conf
from utils import poloniex
import time
import os
 

class Caesar(object):
    def __init__(self, client):
        running_pairs = {}
        balance_ratio = 5
        balance_percentage = 5

        while(True):

            # Sleep, sweetie, sleep...
            time.sleep(5)

            # Handle Poloniex errors
            try:
                ticker = poloniex.get_ticker(client)
                my_orders = poloniex.get_open_orders(client)
                order_book = poloniex.get_order_book(client)
                balances = poloniex.get_balances(client)

            except PoloniexError as e:
               #print "(%s) - Exception: %s : %s" % ('CAESARBOT', e, 
               #                                     self._time())
                continue

            # Operation loop to each pair
            for pair in ticker:
                last = poloniex.last(ticker, pair)

                # STEP 1: CHECK IF PAIR IS NOT RUNNING
                is_running = (pair in running_pairs)
                if is_running:
                    if not running_pairs[pair].isAlive():
                        del running_pairs[pair]

                    continue

                # STEP 2: UPDATE PARAMETERS AND SPECIAL CONDITIONS

                # Parameters
                first_coin = pair.split("_")[0]
                second_coin = pair.split("_")[1]
                lowest_ask = poloniex.lowest_ask(ticker, pair)
                highest_bid = poloniex.highest_bid(ticker, pair)
                first_balance = poloniex.get_balance(balances, first_coin)
                second_balance = poloniex.get_balance(balances, second_coin)
		lowest_24 = poloniex.lowest_24(ticker, pair) 
                open_orders = my_orders[pair]
                balance_avaliable = balance_ratio - len(running_pairs)
                if balance_avaliable <= 0 or float(first_balance) < 0.0001055:
                    continue

                balance = ((first_balance * balance_percentage) 
                            / balance_avaliable)

                # Special conditions
                have_cases_enough = highest_bid * 10000 > 1.0
                exist_open_orders = len(open_orders) > 0
                small_amount = second_balance * highest_bid <= 0.0001

                possible_error = (exist_open_orders or second_balance != 0.0)

                # SPECIAL CONDITION 1: Check if have cases enough
                if not have_cases_enough or first_coin != 'BTC':
                    continue

                # STEP 3: CHECK IF EXISTS ERROR 
                if possible_error:
 
                    # Cancel all existing orders 
                    if exist_open_orders:
                        poloniex.cancel_orders(client, open_orders)

                    #  STEP 3.1: COME BACK TO THE PAIR 
                    if second_balance != 0.0 and not small_amount:
                        print ("(%s) - Possible error, back to pair: %s"
                               % (pair, self._time()))
                        run = Chatuba(client, pair, balance, True)
                        running_pairs[pair] = run
                        run.start()

                else:

                    # STEP 4: CHECK IF CAN ENTER IN PAIR
                    chart_data = client.returnChartData(pair, 300)
                    lo_ma = poloniex.sma(chart_data, 100)
                    hi_ma = poloniex.sma(chart_data, 200)
		    have_bottom = (lowest_ask <= lowest_24)
		    high_marg   = (((lo_ma/lowest_ask)-1)*100) > 4
		    
		    can_enter_strategy = have_bottom and high_marg
                    # STEP 5: VERIFY CONDITIONS AND, IF YES, ENTER IN PAIR
                    if can_enter_strategy:
                        print "(%s) - Enter in pair: %s" % (pair,
                                                            self._time())
                        run = Chatuba(client, pair, balance, False)
                        running_pairs[pair] = run
                        run.start()

    def _time(self):
        return time.asctime(time.localtime(time.time()))


if __name__ == "__main__":
    client = Poloniex(conf.api_key, conf.secret)
 
    try:
        caesar = Caesar(client)
    except KeyboardInterrupt:
        os._exit(1) 
