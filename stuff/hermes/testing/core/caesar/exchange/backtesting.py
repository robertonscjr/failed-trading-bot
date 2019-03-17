from exchange.poloniex import Poloniex
from utils import conf


class Backtesting(object):
    def __init__(self):
        self.client = Poloniex(conf.api_key, conf.secret)
        self.trade_history = client.marketTradeHist(conf.pair) 
        self.chart_data = client.returnChartData(conf.pair, 300)
        self.count = 0
        self.over = False

    def returnTicker(self):
        if self.count >= len(trade_history):
            self.over = False
        else:
            ticker = {'BTC_ETH': {u'last': str(trade_history[self.count]['rate']),
                                  u'quoteVolume': u'0',
                                  u'high24hr': u'0', 
                                  u'isFrozen': u'0', 
                                  u'highestBid': u'0', 
                                  u'percentChange': u'0', 
                                  u'low24hr': u'0',
                                  u'lowestAsk': u'0', 
                                  u'id': 0, 
                                  u'baseVolume': u'0'}}

            count += 1

        if not self.over:
            return None
        else:
            return ticker

    def returnChartData(self, pair, period):
        chart_data = []
        candlestick = {u'volume': u'22.82749524', 
                      u'quoteVolume': u'298.9087607', 
                      u'high': u'0.07647365',
                      u'low': u'0.07634873', 
                      u'date': 1506313500, 
                      u'close': u'0.07642879', 
                      u'weightedAverage': u'0.07636944', 
                      u'open': u'0.07634932'}

        chart_data.append(candlestick)

        return chart_data
