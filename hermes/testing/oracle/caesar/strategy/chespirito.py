from utils import conf
import utils


class Chespirito(object):
    def __init__(self, client):
        self.client = client
        self.bought = False
        self.purchase_price = 0.0

    def purchasable(self):
        if not self.bought and self._last_price() < self._chespirito():
            print "BUY --- last: %.8f - lowest: %.8f" % (self._last_price(), self._chespirito())
            self.bought = True
            self.purchase_price = self._last_price()
        else:
            pass 

    def saleable(self):
        profit_price = self.purchase_price * ((100.0 + conf.fee + conf.profit) / 100.0)
        loss_price = self.purchase_price * ((100.00 - conf.loss) / 100.0)

        if self.bought and self._last_price() > profit_price:
            profit_rate = (self._last_price() / profit_price) * 100.0 - 100.0
            print "SELL --- profit: %.8f" % profit_rate
            self.bought = False

        elif self.bought and self._last_price() < loss_price:
            loss_rate = ((self._last_price() / loss_price) * 100.0 - 100.0)
            print "SELL --- loss: %.8f" % loss_rate
            self.bought = False

        else:
            pass

    def update(self):
        self.ticker = self.client.returnTicker()[conf.pair]

    def _last_price(self):
        return float(self.ticker['last'])

    def _chespirito(self):
        chart = self.client.returnChartData(conf.pair, 300)

        chunked_chart = utils.chunk_list(chart, conf.partitions)

        smallers = []

        for chunked_part in chunked_chart:
            smaller = float(chunked_part[0]['low'])
            for i in range(len(chunked_part)):
                if float(chunked_part[i]['low']) < smaller:
                    smaller = float(chunked_part[i]['low'])

            smallers.append(smaller)

        chespirito = sum(smallers)/len(smallers)

        return chespirito
