from poloniex import Poloniex
from poloniex import PoloniexError
from strategy.pacman import Pacman
from utils import conf
from utils import poloniex
from utils.logger import Log, configure_logging
import time
import os
 

class Caesar(object):
    def __init__(self, client):
        caesar_log = Log("caesar", "logs/caesar.log")
        debug_log = Log("debug", "logs/debug.log")
        configure_logging()
        running_pairs = {}
        minimums = {}
        balance_ratio = 5
        balance_percentage = 5

        while(True):
            # Sleep, sweetie, sleep...
#           time.sleep(5)

            # Handle Poloniex errors
            try:
                ticker = poloniex.get_ticker(client)
                my_orders = poloniex.get_open_orders(client)
                order_book = poloniex.get_order_book(client)
                balances = poloniex.get_balances(client)

            except PoloniexError as e:
                caesar_log.log("(%s) - Exception: %s : %s" % ('CAESARBOT', e, 
                                                               self._time()))
                continue

            # Operation loop to each pair
            for pair in ticker:

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
                open_orders = my_orders[pair]
                balance_avaliable = balance_ratio - len(running_pairs)

              # balance = ((first_balance * balance_percentage) 
              #             / balance_avaliable)

                # Special conditions
                have_cases_enough = highest_bid * 1000 > 1.0
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
                        caesar_log.log("(%s) - Possible error, back to pair: %s" % 
                            (pair, self._time()))

                        run = Pacman(client, pair, 0.00011, True, caesar_log)
                        running_pairs[pair] = run
                        run.start()

                else:

                    # STEP 4: CHECK IF CAN ENTER IN PAIR
                    if float(first_balance) >= 0.00011:
                        chart_data = client.returnChartData(pair, 300)
                        ma_1 = poloniex.ema(chart_data, 3)
                        ma_2 = poloniex.sma(chart_data, 7)
                        ma_3 = poloniex.ema(chart_data, 21)

                        ma = (ma_1 > ma_2 and ma_1 > ma_3)
#                       lo_ma = poloniex.ema(chart_data, 7)
#                       hi_ma = poloniex.ema(chart_data, 21)

                     #  candle_open, candle_close = poloniex.candle_info(
                     #                              client, pair)
                       
                        # 1st CONDITION: Hole
                        hole = (lowest_ask/highest_bid - 1) * 100

                        # 3rd CONDITION: Close greater than open
                     #  candle_ratio = (candle_close / candle_open - 1.0) * 100.0
#                       candle_ratio = (poloniex.last(ticker, pair) / candle_open - 1.0) * 100.0

                        # 4rt CONDITION: Order amount is greater than balance
                        valid_balance = (poloniex.get_first_order_amount(
                                         order_book, pair, 'asks') >= 0.00011)

                     #  debug_log.log("(%s) - Candle ratio: %.2f / Hole: %.2f : %s" % \
                     #                                     (pair,
                     #                                      candle_ratio, 
                     #                                      hole, 
                     #                                      self._time()))

                        debug_log.log("(%s) - EMA(3): %.8f / SMA(7): %.8f / EMA(21): %.8f / Hole: %.2f: %s" % \
                                                          (pair,
                                                           ma_1, 
                                                           ma_2, 
                                                           ma_3,
                                                           hole,
                                                           self._time()))

                        # STEP 5: VERIFY CONDITIONS AND, IF YES, ENTER IN PAIR
                        if (hole < 0.2 and ma and valid_balance):
                           #caesar_log.log("(%s) - Candle ratio: %.2f / Hole: %.2f : %s" % \
                           #                                   (pair,
                           #                                    candle_ratio, 
                           #                                    hole, 
                           #                                    self._time()))

                            caesar_log.log("(%s) - EMA(3): %.8f / SMA(7): %.8f / EMA(21): %.8f : %s" % \
                                                              (pair,
                                                               ma_1, 
                                                               ma_2, 
                                                               ma_3,
                                                               self._time()))

                            debug_log.log("(%s) - Enter in pair: %s" % (pair,
                                                                self._time()))

                            caesar_log.log("(%s) - Enter in pair: %s" % (pair,
                                                                self._time()))

                            run = Pacman(client, pair, 0.00011, False, caesar_log)
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
