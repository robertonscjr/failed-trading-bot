from exchange.backtesting import Backtesting
from exchange.poloniex import Poloniex
from exchange.poloniex import PoloniexError
from strategy.chespirito import Chespirito
from strategy.hole import Hole
from strategy.reverse_hole import ReverseHole
from utils import conf
import time
import os
 

class Caesar(object):
    def __init__(self):
        self.running = []

        while(True):
            for execution in self.running:
                if not execution.is_alive():
                    self.running.delete(execution) 

            if self.signal:
                signal_data = self.read_signal()

                run = Oracle(signal_data) 
                self.running.append(run)
                run.start()

            time.sleep(5)

    def _time(self):
        return time.asctime(time.localtime(time.time()))

    def signal(self):
        return False

    def read_signal(self):
        return {}

 
if __name__ == "__main__":
    try:
        caesar = Caesar()
    except KeyboardInterrupt:
        os._exit(1) 
