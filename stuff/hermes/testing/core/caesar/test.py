from exchange.poloniex import Poloniex
from utils import conf
import os
import time
import datetime

if __name__ == "__main__":
    client = Poloniex(conf.api_key, conf.secret)
    import pdb; pdb.set_trace()
