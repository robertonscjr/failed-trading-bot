from binance.client import Client
from tinydb import TinyDB
import talib
import numpy
from math import ceil


symbol = 'BNBBTC'
api_key = ''
api_secret = ''

client = Client(api_key, api_secret)

orderbook_tickers = TinyDB('logs/orderbook_tickers.db.5').all()

startTime = (int(orderbook_tickers[0]['timestamp']) - 1200) * 1000
endTime = (int(orderbook_tickers[len(orderbook_tickers)-1]['timestamp'] + 600)) * 1000

candlesticks = []
candle_queries = ceil(ceil(ceil(ceil((endTime - startTime)/1000))/60)/500)

for i in range(candle_queries):
    tmp_candlesticks = client.get_historical_klines(
            symbol=symbol,
            interval=Client.KLINE_INTERVAL_1MINUTE,
            start_str=(startTime + 1000 * 500 * 60 * i),
            end_str=(endTime + 1000 * 500 * 60 * i)
        )

    for candle in tmp_candlesticks:
        candle_dict = {
                          "openTime": candle[0],
                          "open": candle[1],
                          "high": candle[2],
                          "low": candle[3],
                          "close": candle[4],
                          "volume": candle[5],
                          "closeTime": candle[6],
                          "quoteAssetVolume": candle[7],
                          "numberOfTrades": candle[8],
                          "takerBuyBaseAssetVolume": candle[9],
                          "takerBuyQuoteAssetVolume": candle[10]
                      }

        if candle_dict not in candlesticks:
            candlesticks.append(candle_dict)

profits = 0
losses = 0
buyPrice = 0
sellPrice = 0
buyed = False

lowestBid = float(orderbook_tickers[0]['bidPrice'])
highestAsk = float(orderbook_tickers[0]['askPrice'])

for ticker in orderbook_tickers:
    askPrice = float(ticker['askPrice'])
    bidPrice = float(ticker['bidPrice'])

    if bidPrice < lowestBid: lowestBid = bidPrice
    if askPrice > highestAsk: highestAsk = askPrice

for ticker in orderbook_tickers: 
    askPrice = float(ticker['askPrice'])
    bidPrice = float(ticker['bidPrice'])
    time = int(ticker['timestamp'])

    sma1 = None
    sma2 = None
    rsi = None

    for index, candle in enumerate(candlesticks):
        closeTime = int(candle['closeTime']/1000)

        if (time-closeTime < 60) and (time-closeTime > 0):
            opens = numpy.array([float(c['open']) \
                                 for c in candlesticks[:index]])

            closes = numpy.array([float(c['close']) \
                                 for c in candlesticks[:index]])

            highs = numpy.array([float(c['high']) \
                                 for c in candlesticks[:index]])

            lows = numpy.array([float(c['low']) \
                                 for c in candlesticks[:index]])

            sma1 = talib.SMA(closes, 2)[len(closes)-1]
            sma2 = talib.SMA(closes, 5)[len(closes)-1]
            rsi = talib.RSI(closes, timeperiod=2)[len(closes)-1]
            sar = talib.SAR(highs, lows, acceleration=0, maximum=0)[len(closes)-1]
            up, mid, low = BBANDS(closes, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
            adx = ADX(highs, lows, closes, timeperiod=14)

            candlesticks = candlesticks[max(0, index - 22):]

#           print("\ncloseTime %d - tickerTime %d - "
#                 "sma1: %.8f - sma2: %.8f" %
#                  (closeTime, time, sma1, sma2))

            if not buyed:
                if sma1 > sma2:
                    buyPrice = askPrice
                    buyed = True
#                    print("buyed")

            elif buyed:
                if (askPrice >= buyPrice * 1.00150):
                    profit = (askPrice / buyPrice) * 100 - 100
                    profits = profits + profit  - 0.075
                    buyed = False

                    print("profit %s" % profit)

                elif sma1 < sma2:# and askPrice <= buyPrice * 0.99925:
                    loss = (askPrice / buyPrice) * 100 - 100
                    losses = losses + loss - 0.075
                    buyed = False
 
                    print("loss %s" % loss)

            break


print("profits: %.3f" % profits)
print("losses: %.3f" % losses)
print("result: %.3f" % (profits+losses))
