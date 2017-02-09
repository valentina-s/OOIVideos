#rom urlparse import urlparse
#from threading import threading
#import httplib, sys
#from Queue import Queue
import urllib.request
from skimage import io

import dask.array as da
from dask import delayed

import numpy as np

import time

def testWithDask(list_urls):

    res = urllib.request.Request(list_urls[0])
    image = io.imread(list_urls[0])
    print(image.dtype)
    print(image.shape)

    imread =  delayed(io.imread, pure=True)
    lazy_values = [imread(url) for url in list_urls]
    arrays = [da.from_delayed(lazy_value, dtype=image.dtype, shape=image.shape) for lazy_value in lazy_values]
    stack = da.stack(arrays, axis=0)
    print(stack.shape)
    print(type(stack))
    res = stack.mean().compute()
    print(res)
    return(res)

def testWithMap(list_urls):

    import concurrent.futures
    import urllib.request

    e = concurrent.futures.ProcessPoolExecutor(max_workers=1)
    stack = e.map(io.imread,list_urls)
    print(np.array(list(stack)).shape)
    return(stack)


if __name__ == "__main__":
    import sys
    IPAddress = sys.argv[1]

    # create a list of paths to call
    base_url = 'http://'+IPAddress+'/org/oceanobservatories/rawdata/files/RS03ASHS/PN03B/06-CAMHDA301/2016/09/01/CAMHDA301-20160901T000000Z.mov/frame/'
    list_urls = [base_url+str(frame) for frame in range(1,25000,100)]
    t = time.time()
    res = testWithMap(list_urls)
    print(time.time() - t)
