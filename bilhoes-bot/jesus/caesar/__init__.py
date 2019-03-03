from exchange.poloniex import Poloniex
from exchange.poloniex import PoloniexError
from utils import conf
from utils import poloniex
from utils.logger import Log, configure_logging
import time
import os
 

class Caesar(object):
    def __init__(self, client):
        caesar_log = Log("caesar", "logs/caesar.log")
        configure_logging()

        pair = 'USDT_BTC'
        candle_time = 900

        is_running = False
        bought = False
        target_time = client.returnChartData(pair, candle_time)[-1]['date'] + candle_time

        while(True):
            this_time = time.time()
            if this_time < target_time:
                continue
            else:
                target_time += candle_time
            
            try:
                ticker = poloniex.get_ticker(client)
                my_orders = poloniex.get_open_orders(client)
                order_book = poloniex.get_order_book(client)
                balances = poloniex.get_balances(client)

            except PoloniexError as e:
                continue

            chart_data = client.returnChartData(pair, candle_time)

            first_data = [float(chart['close']) for chart in chart_data[:len(chart_data)-1]]
            second_data = [float(chart['close']) for chart in chart_data[:len(chart_data)-2]]
            third_data = [float(chart['close']) for chart in chart_data[:len(chart_data)-3]]

            first_ema = poloniex.ema(first_data, 3)
            second_ema = poloniex.ema(second_data, 3)
            third_ema = poloniex.ema(third_data, 3)

            buy_signal = first_ema > second_ema and second_ema < third_ema
            sell_signal = first_ema < second_ema 


            if buy_signal and not bought:
                caesar_log.log("(%s) - 1st: %.8f / 2nd: %.8f / 3rd: %.8f : %s"
                           % (pair,
                              first_ema, 
                              second_ema, 
                              third_ema, 
                              self._time()))
                caesar_log.log("(%s) - Enter in pair : %s" % (pair, 
                                                             self._time()))

                first_coin = pair.split("_")[0]
                highest_bid = poloniex.highest_bid(ticker, pair)
                balance = poloniex.get_balance(balances, first_coin)
                buy_price = highest_bid + 0.00000001
                amount = (balance / buy_price)

                caesar_log.log("(%s) - Executing buy order at %.8f with %.5f of amount : %s"
                               % (pair,
                                  highest_bid,
                                  balance,
                                  self._time()))

            #   buy_id = str(client.buy(pair,
            #                           buy_price,
            #                           amount)['orderNumber'])

                fake = False
                while True:
                    trade_history = client.returnTradeHistory(pair)
                    for history in trade_history:
                        if fake:
                            bought = True

#                       if history['orderNumber'] == buy_id: 
#                           bought = True

                    if bought:
                        break

                    order_book = client.returnOrderBook(pair, 5)
                    last_buy_order = float(order_book['bids'][0][0])
                    if buy_price < last_buy_order:
#                       client.cancelOrder(buy_id)

                        buy_price = last_buy_order + 0.00000001
                        amount = (balance / buy_price)

                        caesar_log.log("(%s) - Executing buy order at %.8f with %.5f of amount : %s"
                                       % (pair,
                                          buy_price, 
                                          balance,
                                          self._time()))

                        fake = True
#                       buy_id = str(client.buy(pair,
#                                               buy_price,
#                                               amount)['orderNumber'])

                caesar_log.log("(%s) - Bought! : %s" % (pair, 
                                                        self._time()))
                        

            if sell_signal and bought:
                caesar_log.log("(%s) - 1st: %.8f / 2nd: %.8f / 3rd: %.8f : %s"
                           % (pair,
                              first_ema, 
                              second_ema, 
                              third_ema, 
                              self._time()))
                caesar_log.log("(%s) - Leaving the pair: %s" % (pair, 
                                                                self._time()))

                second_coin = pair.split("_")[1]
                lowest_ask = poloniex.lowest_ask(ticker, pair)
                balance = poloniex.get_balance(balances, second_coin)
                sell_price = lowest_ask - 0.00000001

                caesar_log.log("(%s) - Executing sell order at %.8f with %.5f of amount : %s"
                               % (pair,
                                  sell_price,
                                  balance,
                                  self._time()))

             #  sell_id = str(client.sell(pair,
             #                            sell_price,
             #                            amount)['orderNumber'])

                fake = False
                sold = False
                while True:
                    trade_history = client.returnTradeHistory(pair)
                    for history in trade_history:
                        if fake:
                            bought = False
                            sold = True

#                       if history['orderNumber'] == sell_id: 
#                           bought = False
#                           sold = True

                    if sold:
                        break

                    order_book = client.returnOrderBook(pair, 5)
                    last_sell_order = float(order_book['asks'][0][0])
                    if sell_price > last_sell_order:
#                       client.cancelOrder(sell_id)

                        sell_price = last_sell_order - 0.00000001

                        caesar_log.log("(%s) - Executing sell order at %.8f with %.5f of amount : %s"
                                       % (pair,
                                          sell_price,
                                          balance,
                                          self._time()))

                        fake = True
#                       sell_id = str(client.sell(pair,
#                                                 sell_price,
#                                                 balance)['orderNumber'])

                caesar_log.log("(%s) - Sold! : %s" % (pair, 
                                                      self._time()))

    def _time(self):
        return time.asctime(time.localtime(time.time()))


if __name__ == "__main__":
    client = Poloniex(conf.api_key, conf.secret)
 
    try:
        caesar = Caesar(client)
    except KeyboardInterrupt:
        os._exit(1) 
