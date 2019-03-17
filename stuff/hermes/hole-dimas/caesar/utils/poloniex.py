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

def get_day_volume(client):
    return client.return24hVolume()

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
    candlestick = client.returnChartData(pair, 300)
    candle = candlestick[len(candlestick)-1]
    candle_open = float(candle['open'])
    candle_close = float(candle['close'])

    return candle_open, candle_close

def get_first_order_amount(order_book, pair, order_type):
    return order_book[pair][order_type][0][1]

def get_first_order_price(order_book, pair, order_type):
    return float(order_book[pair][order_type][0][0])

def sma(chart_data, period):
    average = 0.0
    for i in range(period):
        average = average + float(chart_data[len(chart_data)-1-i]['close'])

    return average / float(period)

def ema(chart_data, period):
    for k in range(1,len(chart_data)):
        chart_data_organized.append(chart_data[k-1]['close'])
    
    alpha = 2/(period +1.0)
    alpha_rev = 1-alpha
    chart_data_fl = np.array(chart_data_organized,dtype=float)
    n = chart_data_fl.shape[0]

    pows = alpha_rev**(np.arange(n+1))

    scale_arr = 1/pows[:-1]
    offset = chart_data_fl[0]*pows[1:]
    pw0 = alpha*alpha_rev**(n-1)

    mult = chart_data_fl*pw0*scale_arr
    cumsums = mult.cumsum()
    out = offset + cumsums*scale_arr[::-1]
    out_float = float(out[-1])
    return out_float

def candle_size(self,candle): 
    open_candle = float(candle['open'])
    close_candle = float(candle['close'])
	
    return ((close_candle / open_candle)-1.0) * 100
    
def candle_gigante(self,candle):
    first_candle = self.candle_size(candle[0])
    second_candle = self.candle_size(candle[1])

    if (first_candle > 0) and (second_candle < 0) \
                          and (first_candle > (2 * abs(second_candle) )):
        return True       
    
def candle_hammer(self,candle):
    first_candle = self.candle_size(candle[0])
    second_candle = self.candle_size(candle[1])
	
    pen_candle = float(candle[0]['open'])
    head = float(candle[0]['high'])
    tail = float(candle[0]['low'])

    if (first_candle > 0) and (second_candle < 0) \
                 	  and (open_candle > tail*1.4):
        return True       
