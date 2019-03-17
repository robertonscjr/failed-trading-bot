from exchange.poloniex import Poloniex
from exchange.poloniex import PoloniexError
from strategy.pacman import Pacman
from utils import conf
from utils import poloniex
import time
import os
import shutil
import sys

def run_backtest(pair, client, strategy, candle_time, start, end,
                 ema1, ema2, sma):

    coin = pair.split("_")[1]
    name = "%s_%s-%s-%s-%s" % (strategy,
                               ema1,
                               ema2,
                               sma,
                               candle_time)

    log = open("logs/%s/%s" % (name, coin), "w")

    operations = []
    buys = []
    sells = []
    ratios = []

    chart_all = client.returnChartData(pair, candle_time, start, end)

    # Record all buys and sells signals
    last_buy = 0.0
    bought = False
    for i in range(1, days * 96):
        chart_data = chart_all[:-(days * 96 - i)]
        calc_data = chart_data[:len(chart_data)-1]
        last_close = float(calc_data[len(calc_data)-1]['close'])
  
        closes = [float(chart['close']) for chart in calc_data]
        
        ema_1 = poloniex.ema(closes, ema1)
        ema_2 = poloniex.ema(closes, ema2)
#       wma = poloniex.wma(calc_data, ema2)

        if last_buy == 0.0:
            stop = 0.0
        else:
            stop = (last_close / last_buy) * 100.0 - 100.0

        buy_signal = (ema_1 > ema_2)
        sell_signal = (ema_1 < ema_2)

        if not bought:
            if buy_signal:
                buys.append(chart_data[len(chart_data)-1])
                last_buy = float(chart_data[len(chart_data)-1]['open'])
                bought = True

        if sell_signal and bought:
            sells.append(chart_data[len(chart_data)-1])
            bought = False

    # Calculates all ratios
    last_sell = int(sells[0]['date'])
    for buy_signal in buys:

        # Avoid a time-impossible profit
        if int(buy_signal['date']) < last_sell:
            continue

        for sell_signal in sells:
            if int(sell_signal['date']) > int(buy_signal['date']):
                ratio = ((float(sell_signal['open']) 
                          / float(buy_signal['open'])) * 100 - 100)

                buy_time = time.strftime("%D %H:%M", 
                               time.localtime(int(buy_signal['date'])))

                sell_time = time.strftime("%D %H:%M",
                               time.localtime(int(sell_signal['date'])))

                operations.append({'buy_time': buy_time,
                                   'sell_time': sell_time,
                                   'ratio': ratio})

                last_sell = int(sell_signal['date'])
                ratios.append(ratio)
                break

    # Separates profits and losses
    profits = [op for op in operations if op['ratio'] > 0.0]
    losses = [op for op in operations if op['ratio'] <= 0.0]

    log.write("--------- Profits ---------\n")
    for profit in profits:
        log.write("Sell: %s - Buy: %s - Ratio: %.2f\n" 
                  % (profit['sell_time'],
                     profit['buy_time'],
                     profit['ratio']))

    log.write("\n--------- Losses ---------\n")
    for loss in losses:
        log.write("Sell: %s - Buy: %s - Ratio: %.2f\n" % (loss['sell_time'],
                                                          loss['buy_time'],
                                                          loss['ratio']))

    log.close()

    return operations


if __name__ == "__main__":
    print "----- BEGIN -----"

    client = Poloniex(conf.api_key, conf.secret)
    pairs = [pair
             for pair in client.returnTicker().keys()
             if (pair.split("_")[0] == 'BTC')]

#   ema1 = 16
#   ema2 = 42
#   sma = 52
#   maximum = max(ema1, ema2, sma) * 2
#   candle_time = 900
#   days = 30
#   end = time.time()
#   start = end - candle_time * (maximum + 96 * days)
    
    if len(sys.argv) != 7:
        print "Wrong parameters!"
        print "Parameters: strategy ema1 ema2 sma candle days"
        sys.exit()

    # Parameters 
    strategy = sys.argv[1]
    ema1 = int(sys.argv[2])
    ema2 = int(sys.argv[3])
    sma = int(sys.argv[4])
    maximum = max(ema1, ema2, sma) * 2
    candle_time = int(sys.argv[5])
    days = int(sys.argv[6])
    end = time.time()
    start = end - candle_time * (maximum + 96 * days)

    name = "%s_%s-%s-%s-%s" % (strategy,
                               ema1,
                               ema2,
                               sma,
                               candle_time)

    path = "logs/%s" % name
    if os.path.exists(path):
        print "Remove directory"
        shutil.rmtree(path)

    print "Create directory"
    os.mkdir(path)

    log = open("%s/ALL" % path, "w")

    print "Run backtest, please wait"
    operations = {}
    for pair in pairs:
        coin = pair.split("_")[1]

        operations[pair] = run_backtest(pair,
                                        client,
                                        strategy,
                                        candle_time,
                                        start,
                                        end,
                                        ema1,
                                        ema2,
                                        sma)

        sum_ratios = sum([float(operation['ratio'])
                         for operation in operations[pair]])

        print coin, sum_ratios

    print "Saving ratios of all coins"
    log.write("--------- Ratios ---------\n")
    sum_all = 0.0
    for pair in pairs:
        coin = pair.split("_")[1]
        sum_ratios = sum([float(operation['ratio'])
                         for operation in operations[pair]])

        sum_all += sum_ratios
        log.write("%5s: %.2f\n" % (coin, sum_ratios))

    ratio_all = sum_all / len(pairs)
    log.write("%5s: %.2f\n" % ("TOTAL", ratio_all))
    log.close()

    import pdb; pdb.set_trace()

    print "------- END -------"
