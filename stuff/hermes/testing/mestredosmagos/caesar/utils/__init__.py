import math
import time


def chunk_list(iterable, n):
    chunk_size = int(math.ceil(len(iterable) / n))
    chunked = (iterable[i * chunk_size:i * chunk_size + chunk_size] 
               for i in range(n))

    return list(chunked)

def time():
    return time.asctime(time.localtime(time.time()))
