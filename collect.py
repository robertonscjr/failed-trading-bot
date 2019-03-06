from binance.client import Client
from time import time
from tinydb import TinyDB
from requests.exceptions import RequestException


symbol = 'BNBBTC'
api_key = ''
api_secret = ''

client = Client(api_key, api_secret)

orderbook_ticker_db = TinyDB('orderbook_tickers.db')
#trade_history_db = TinyDB('trade_history.db')
#candlesticks_db = TinyDB('candlesticks.db')

status_code = 200
while(status_code != 429):
    try:
        start_time = time()

        # Candlesticks
#       candlesticks = client.get_klines(
#           symbol=symbol,
#           interval=Client.KLINE_INTERVAL_1MINUTE,
#           limit=100
#       )
#
#       for candle in candlesticks:
#           candle_dict = {
#                             "openTime": candle[0],
#                             "open": candle[1],
#                             "high": candle[2],
#                             "low": candle[3],
#                             "close": candle[4],
#                             "volume": candle[5],
#                             "closeTime": candle[6],
#                             "quoteAssetVolume": candle[7],
#                             "numberOfTrades": candle[8],
#                             "takerBuyBaseAssetVolume": candle[9],
#                             "takerBuyQuoteAssetVolume": candle[10]
#                         }
#
#           tmp_candlesticks = candlesticks_db.all()[-200:]
#           if candle_dict not in tmp_candlesticks:
#               candlesticks_db.insert(candle_dict)
#
#       # Trade History
#       trade_history = client.get_recent_trades(symbol=symbol, limit=100)
#
#       tmp_trade_history = trade_history_db.all()[-200:]
#       for trade in trade_history:
#           if trade not in tmp_trade_history:
#               trade_history_db.insert(trade)

        # Order Book Ticker
        orderbook_ticker = client.get_orderbook_ticker(symbol=symbol)
        orderbook_ticker['timestamp'] = time()

        orderbook_ticker_db.insert(orderbook_ticker)

        end_time = time()

        elapsed_time = end_time - start_time

        print("info registered at %d seconds" % elapsed_time)

    except RequestException as e:
        pass

    except Exception as e:
        status_code = e.status_code
