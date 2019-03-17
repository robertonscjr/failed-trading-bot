from exchange.poloniex import Poloniex
from exchange.poloniex import PoloniexError
from strategy.pacman import Pacman
from utils import conf
from utils import poloniex
from utils.logger import Log, configure_logging
import time
import os

 
PAIR = 'BTC_ETH'
CANDLE_TIME = 900
DAYS = 30
HISTORIC_PERIOD = 96 * DAYS

EMA1_PERIOD = 16
EMA2_PERIOD = 42
SMA_PERIOD = 52
MAX_PERIOD = 120

class Caesar(object):
    def __init__(self, client):
        pairs = client.returnTicker().keys()
        sum_profits = 0
        operations = {}
        f = open("logs/combanda16comstop", "w")

        for pair in pairs:
            first_coin = pair.split("_")[0]
            if first_coin != 'BTC':
                continue

            operations[pair] = []
           
            end = time.time()
#           end = 1514764799
#           end = 1512086399
#           end = 1509494399
            start = end - CANDLE_TIME * (MAX_PERIOD + HISTORIC_PERIOD)

            chart_all = client.returnChartData(pair, CANDLE_TIME, start, end)

            buys = []
            sells = []
            profits = []

            last_buy = 0.0
            for i in range(1, HISTORIC_PERIOD):
                chart_data = chart_all[:-(HISTORIC_PERIOD - i)]
                last_close = float(chart_data[len(chart_data) - 2]['close'])

                data = [float(chart['close']) for chart in chart_data[:len(chart_data)-1]]
                ema_1 = poloniex.ema(data, EMA1_PERIOD)
                ema_2 = poloniex.ema(data, EMA2_PERIOD)
                sma = poloniex.sma(data, SMA_PERIOD)

                top, mid, bot = poloniex.bollinger(chart_data[:len(chart_data)-1], 26)

                stop = (last_buy / last_close) * 100.0 - 100.0

                buy_signal = (ema_1 > ema_2) and last_close > ema_2 and last_close > top
                sell_signal = (ema_1 < ema_2) or last_close < ema_2 or stop > 5.0

                buy_time = time.strftime("%D %H:%M", time.localtime(int(chart_data[len(chart_data)-1]['date'])))
#               print "ema1:%.8f - ema2:%.8f - sma:%.8f - %s" % (ema_1, ema_2, sma, buy_time)
#               import pdb; pdb.set_trace()
                if buy_signal:
                    buys.append(chart_data[len(chart_data)-1])
                    last_buy = float(chart_data[len(chart_data)-1]['open'])

                if sell_signal:
                    sells.append(chart_data[len(chart_data)-1])

            last_sell = int(sells[0]['date'])
            for buy_signal in buys:
                if int(buy_signal['date']) < last_sell:
                    continue

                for sell_signal in sells:
                    if int(sell_signal['date']) > int(buy_signal['date']):
                        ratio = (float(sell_signal['open']) / float(buy_signal['open'])) * 100 - 100

                        buy_time = time.strftime("%D %H:%M", time.localtime(int(buy_signal['date'])))
                        sell_time = time.strftime("%D %H:%M", time.localtime(int(sell_signal['date'])))
                        operations[pair].append({'buy_time': buy_time, 'sell_time': sell_time, 'ratio': ratio})

                        last_sell = int(sell_signal['date'])
                        profits.append(ratio)
                        break

            sum_profits = sum_profits + sum(profits)
            print("%9s: %.2f" % (pair, sum(profits)))
            f.write("%9s: %.2f\n" % (pair, sum(profits)))

        avg_profits = sum_profits / len(operations)
        print("    TOTAL: %.2f" % avg_profits)
        f.write("    TOTAL: %.2f\n" % avg_profits)
        f.close()
        import pdb; pdb.set_trace()
          
    def _time(self):
        return time.asctime(time.localtime(time.time()))


if __name__ == "__main__":
    client = Poloniex(conf.api_key, conf.secret)
 
    try:
        caesar = Caesar(client)
    except KeyboardInterrupt:
        os._exit(1) 
