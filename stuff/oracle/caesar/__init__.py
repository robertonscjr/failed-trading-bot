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
MAX_PERIOD = 120 * 4

class Caesar(object):
    def __init__(self, client):
        pairs = client.returnTicker().keys()
        sum_profits = 0

        for pair in pairs:
            first_coin = pair.split("_")[0]
            if first_coin != 'USDT':
                continue
           
            end = time.time()
            start = end - CANDLE_TIME * (MAX_PERIOD + HISTORIC_PERIOD)

            chart_all = client.returnChartData(pair, CANDLE_TIME, start, end)

            buys = []
            sells = []
            profits = []

            for i in range(1, HISTORIC_PERIOD):
                chart_data = chart_all[:len(chart_all) - HISTORIC_PERIOD + i]
                last_close = float(chart_data[len(chart_data)-2]['close'])

                ema_1 = poloniex.ema(chart_data, EMA1_PERIOD)
                ema_2 = poloniex.ema(chart_data, EMA2_PERIOD)
                sma = poloniex.sma(chart_data, SMA_PERIOD)

                top, mid, bot = poloniex.bollinger(chart_data, SMA_PERIOD)

                buy_signal = (ema_1 > ema_2 and ema_1 > sma)# and last_close > top
                sell_signal = (ema_1 < ema_2 and ema_1 < sma) and last_close < mid

                if buy_signal:
                    buys.append(chart_data[len(chart_data)-1])

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
#                       print ("BUY(%s): %.8f - SELL(%s): %.8f - RATIO: %.2f"
#                              % (buy_time,
#                                float(buy_signal['open']),
#                                sell_time,
#                                float(sell_signal['open']),
#                                ratio))
#
                        last_sell = int(sell_signal['date'])
                        profits.append(ratio)
                        break

                sum_profits = sum_profits + sum(profits)                      

            date_buys = [buy['date'] for buy in buys]
            date_sells = [sell['date'] for sell in sells]

            print "%s: %.2f" % (pair, sum(profits))

        print "total: %.2f" % sum_profits
        import pdb; pdb.set_trace()
          
    def _time(self):
        return time.asctime(time.localtime(time.time()))


if __name__ == "__main__":
    client = Poloniex(conf.api_key, conf.secret)
 
    try:
        caesar = Caesar(client)
    except KeyboardInterrupt:
        os._exit(1) 
