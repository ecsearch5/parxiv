import warnings
warnings.filterwarnings("ignore")

import urllib3
from src.logger import *


END_OF_STREAM = b''


class Connector(object):
    logger = None
    conn = None
    def __init__(self, name="connector", log_dir="./log", use_proxy=True, proxy_url=None):
        self.name = name
        self.log_dir = log_dir
        self.use_proxy = use_proxy
        self.proxy_url = proxy_url
        self.logger = ClassicLogger(name=self.name, to_file=True, to_dir=self.log_dir)
        if self.use_proxy and self.proxy_url is not None:
            self.conn = urllib3.ProxyManager(proxy_url=self.proxy_url, num_pools=100, block=True)
        else:
            self.conn = urllib3.PoolManager(num_pools=100, block=True)

    def simple_get(url):
        resp = self.conn.request("GET", url)
        return resp.data.decode('utf-8')

    def stream_to_buffer(self, method, url, chunk_length=1024, fields=None, headers=None, callback=None):
        resp = self.conn.request(method=method, url=url,
                                 preload_content=False,
                                 fields=fields, headers=headers)
        arr = resp.read(chunk_length)
        if callback is not None:
            callback(arr)
        while True:
            arr = resp.read(chunk_length)
            if arr is None or arr == END_OF_STREAM:
                break
            if callback is not None:
                callback(arr)
        resp.release_conn()


def file_callback(fp):
    def _callback(arr):
        if isinstance(arr, bytes):
            fp.write(arr)

    return _callback


def buffer_callback(buf):
    def _callback(arr):
        if isinstance(arr, bytes):
            buf += arr
    return _callback

