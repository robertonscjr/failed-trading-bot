from exchange.poloniex import Poloniex
from exchange.poloniex import PoloniexError
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

            # Handle Poloniex errors
            try:
                ticker = poloniex.get_ticker(client)
                my_orders = poloniex.get_open_orders(client)
                order_book = poloniex.get_order_book(client)
                balances = poloniex.get_balances(client)

            except PoloniexError as e:
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
                last = poloniex.last(ticker, pair)
                lowest_ask = poloniex.lowest_ask(ticker, pair)
                highest_bid = poloniex.highest_bid(ticker, pair)
                first_balance = poloniex.get_balance(balances, first_coin)
                second_balance = poloniex.get_balance(balances, second_coin)
                open_orders = my_orders[pair]
                balance_avaliable = balance_ratio - len(running_pairs)

                # Special conditions
#               have_cases_enough = highest_bid * 1000000 > 1.0
                exist_open_orders = len(open_orders) > 0
                small_amount = second_balance * highest_bid <= 0.0001

                possible_error = (exist_open_orders or second_balance >= 0.0001)
                forbidden_pairs = []
               
                # SPECIAL CONDITION 1: Check if have cases enough
                if first_coin != 'BTC' or (pair in forbidden_pairs):
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

                        amount_buy = float(first_balance/(67-len(running_pairs)))
                        run = Pacman(client, pair, amount_buy, True, caesar_log)
                        running_pairs[pair] = run
                        run.start()

                else:

                    # STEP 4: CHECK IF CAN ENTER IN PAIR
                    if float(first_balance) >= 0.00011:
                        timestamp = time.time()
                        timestamp_range = timestamp - (900 * 320)
                        chart_data = client.returnChartData(pair, 900, timestamp_range, timestamp)

                        data = [float(chart['close']) for chart in chart_data[:len(chart_data)-1]]
                        ma_1 = poloniex.ema(data, 16)
                        ma_2 = poloniex.sma(data, 52)
                        ma_3 = poloniex.ema(data, 42)

                        debug_log.log("(%s) - EMA(16): %.8f / SMA(52): %.8f / EMA(42): %.8f: %s" % \
                                                          (pair,
                                                           ma_1, 
                                                           ma_2, 
                                                           ma_3,
                                                           self._time()))

                        buy_signal = (ma_1 > ma_2 and ma_1 > ma_3)

                        # STEP 5: VERIFY CONDITIONS AND, IF YES, ENTER IN PAIR
                        if buy_signal:
                            caesar_log.log("(%s) - EMA(16): %.8f / SMA(52): %.8f / EMA(42): %.8f : %s" % \
                                                              (pair,
                                                               ma_1, 
                                                               ma_2, 
                                                               ma_3,
                                                               self._time()))

                            debug_log.log("(%s) - Enter in pair: %s" % (pair,
                                                                self._time()))

                            caesar_log.log("(%s) - Enter in pair: %s" % (pair,
                                                                self._time()))

                            amount_buy = float(first_balance/(67-len(running_pairs)))
                            run = Pacman(client, pair, amount_buy, False, caesar_log)
                            running_pairs[pair] = run
                            run.start()

            time.sleep(30)

    def _time(self):
        return time.asctime(time.localtime(time.time()))


if __name__ == "__main__":
    client = Poloniex(conf.api_key, conf.secret)
 
    try:
        caesar = Caesar(client)
    except KeyboardInterrupt:
        os._exit(1) 
