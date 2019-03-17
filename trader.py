from binance.client import Client
from requests.exceptions import RequestException
from tinydb import TinyDB
import talib
import numpy
from math import ceil
import time
from binance.enums import *


def log(message):
    with open("trader.log", "a+") as f:
        f.write(message + "\n")

    print(message)

first_coin = 'BNB'
second_coin = 'BTC'
symbol = first_coin + second_coin
api_key = 'safa'
api_secret = 'sfasfs'

client = Client(api_key, api_secret)

buyed = False
buy_price = None
profits = 0

status_code = 200

message = "START TRADER"
log(message)

while(status_code != 429):
    try:
        ticker = client.get_ticker(symbol=symbol)
        first_balance = float(client.get_asset_balance(asset=first_coin,
                                             recvWindow=300000)['free'])

        second_balance = float(client.get_asset_balance(asset=second_coin,
                                             recvWindow=300000)['free'])

        price_change = float(ticker['priceChangePercent'])
        ask_price = float(ticker['askPrice'])
        bid_price = float(ticker['bidPrice'])

        if not buyed:
#           if price_change > 0.0:
            if True:
                buy_price = ask_price
                amount = round((0.0015 / buy_price), 2)

                order = client.create_order(
                            symbol='BNBBTC',
                            side=SIDE_BUY,
                            type=ORDER_TYPE_MARKET,
                            quantity=amount,
                            recvWindow=300000)

                buyed = True
                message = ("\nBUY %.2f AT %.8f" % (amount, buy_price))
                log(message)

        else:
            if (bid_price >= buy_price * 1.0015):
                amount = round(first_balance - 0.01, 2)
  
                order = client.create_order(
                            symbol='BNBBTC',
                            side=SIDE_SELL,
                            type=ORDER_TYPE_MARKET,
                            quantity=amount,
                            recvWindow=300000)

                profit = (bid_price / buy_price) * 100 - 100
                profits = profits + profit  - 0.075
                buyed = False
                message = ("SELL AT %.8f / PROFIT:%.3f - TOTAL P.:%.3f"
                           % (bid_price, profit, profits))
                log(message)

    except RequestException as e:
        message = "ERROR %s" % e
        log(message)
        pass

    except Exception as e:
        message = "ERROR %s" % e
        log(message)

        status_code = e.status_code

message = "QUIT"
log(message)
