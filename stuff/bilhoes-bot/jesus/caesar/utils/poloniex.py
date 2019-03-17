import numpy as np
import math

def last(ticker, pair):
    last = float(ticker[pair]['last'])

    return last

def highest_bid(ticker, pair):
    highest_bid = float(ticker[pair]['highestBid'])

    return highest_bid

def lowest_ask(ticker, pair):
    lowest_ask = float(ticker[pair]['lowestAsk'])

    return lowest_ask 

def get_balance(balances, coin):
    balance = float(balances[coin])

    return balance

def get_ticker(client):
    return client.returnTicker()

def get_order_book(client):
    return client.returnOrderBook('all', 1)

def get_open_orders(client):
    return client.returnOpenOrders('all')

def get_balances(client):
    return client.returnBalances()

def update_minimums(ticker, client):
    minimum = {}

    for pair in ticker:
        candlestick = client.returnChartData(pair, 300)
        candle = candlestick[len(candlestick)-1]
        minimum[pair] = float(candle['open'])

    return minimum

def cancel_orders(client, orders):
    for order in orders:
        client.cancelOrder(order['orderNumber'])

def candle_info(client, pair):
    candlestick = client.returnChartData(pair, 1800)
    candle = candlestick[len(candlestick)-1]
    candle_open = float(candle['open'])
    candle_close = float(candle['close'])

    return candle_open, candle_close

def get_first_order_amount(order_book, pair, order_type):
    return order_book[pair][order_type][0][1]

def get_first_order_price(order_book, pair, order_type):
    return float(order_book[pair][order_type][0][0])

def sma(data, period):
    summation = 0.0
    summation = sum([close for close in data])

    return summation / float(period)

def bollinger(chart_data, period):
    top = 0.0
    bot = 0.0
    data = [float(chart['close']) for chart in chart_data]
    mid = sma(data, period)

    closes = []
    for i in range(len(chart_data)):
        closes.append(float(chart_data[len(chart_data)-1-i]['close']))

    std_sum = 0.0
    for i in range(period):
        data = [float(chart['close']) for chart in chart_data[len(chart_data)-i-period:len(chart_data)-i]]
        std_sma = sma(data, period)
        std_sum += (closes[i] - std_sma) ** 2

    std_avg = std_sum / period
    std = math.sqrt(std_avg)

    top = mid + 2 * std
    bot = mid - 2 * std 

    return top, mid, bot

def ema(data, period):
    alpha = 2.0 / (period + 1.0)
    ema = data.pop(0)

    for close in data:
        ema = alpha * close + (1.0 - alpha) * ema

    return ema
        
#   ema = float(data[len(data) - int(period) - 1])
#
#   k = 2.0/(float(period) + 1.0)
#   for i in range(1, period):
#       close = float(data[len(data) - int(period) - 1 + i])
#       ema = (close - ema) * k + ema
#
#   return ema

#   window = period
#   if len(data) < window + 2:
#       return None
#   c = 2 / float(window + 1)
#   if not previous_ema:
#       return ema(data, window, window, sma(data[-window*2 + 1:-window + 1], window))
#   else:
#       current_ema = (c * data[-position]) + ((1 - c) * previous_ema)
#       if position > 0:
#           return ema(data, window, position - 1, current_ema)
#       return previous_ema

#   window = float(period)
#
#   if len(data) < 2 * window:
#       raise ValueError("data is too short")
#   c = 2.0 / (window + 1.0)
#   current_ema = sma(data[-window*2:-window], window)
#   for value in data[-window:]:
#       current_ema = (c * value) + ((1.0 - c) * current_ema)
#   return current_ema 
#    
