from exchange.poloniex import Poloniex
from exchange.poloniex import PoloniexError
from strategy.pacman import Pacman
from utils import conf
from utils import poloniex
from utils.logger import Log, configure_logging
from threading import Thread
import time
import os

 

if __name__ == "__main__":
    client = Poloniex(conf.api_key, conf.secret)
 
    try:
        ema1 = 8
        ema2 = 21
        sma = 26
        days = 30
        candle_time = 900
        historic_period = 96 * days
        end = time.time()
        start = end - candle_time * (30 + historic_period)
        pairs = client.returnTicker().keys()

        print "Run experiments"
        for i in range(1,4):
            print "Experiment no %d" % i
            ema1_period = ema1 * i
            ema2_period = ema2 * i
            sma_period = sma * i

            name = "%d-%d-%d-simplecross-boll-stop" % (ema1_period, ema2_period, sma_period)

            sum_profits = 0
            operations = {}

            f = open("logs/%s" % name, "w")

            for pair in pairs:
                if pair != 'BTC_CVC':
                    continue

                first_coin = pair.split("_")[0]
                if first_coin != 'BTC':
                    continue

                operations[pair] = []

                chart_all = client.returnChartData(pair, candle_time, start, end)
                buys = []
                sells = []
                profits = []

                last_buy = 0.0
                for i in range(1, historic_period):
                    chart_data = chart_all[:-(historic_period - i)]
                    last_close = float(chart_data[len(chart_data) - 2]['close'])

                    data = [float(chart['close']) for chart in chart_data[:len(chart_data)-1]]
                    ema_1 = poloniex.ema(data[-ema1_period:], ema1_period)
                    ema_2 = poloniex.ema(data[-ema2_period:], ema2_period)
                    sma = poloniex.sma(data[-sma_period:], sma_period)

#                   top, mid, bot = poloniex.bollinger(chart_data[:len(chart_data)-1], 26)

                    stop = (last_buy / last_close) * 100.0 - 100.0

                    buy_signal = (ema_1 > ema_2) and last_close > ema_2# and last_close > top
                    sell_signal = (ema_1 < ema_2) or last_close < ema_2 or stop > 5.0

                    buy_time = time.strftime("%D %H:%M", time.localtime(int(chart_data[len(chart_data)-1]['date'])))
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
                print("%s - %9s: %.2f" % (name, pair, sum(profits)))
                f.write("%s - %9s: %.2f\n" % (name, pair, sum(profits)))

            avg_profits = sum_profits / len(operations)
            print("%s -   TOTAL: %.2f" % (name, avg_profits))
            f.write("%s -   TOTAL: %.2f\n" % (name, avg_profits))
            f.close()

    except KeyboardInterrupt:
        os._exit(1) 
