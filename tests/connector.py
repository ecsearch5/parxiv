import unittest
from src.connection import *
import json


class ConnTest(unittest.TestCase):

    def setUp(self):
        self.conn = Connector(use_proxy=False)

    def tearDown(self):
        pass

    def testDownload(self):
        url = "https://httpbin.org/ip"
        f = open("test.json", "wb+")
        self.conn.stream_to_buffer("GET", url, callback=file_callback(f))
        f.close()

        obj = json.load(open("test.json", "r"))
        self.assertTrue("origin" in obj.keys())


if __name__ == '__main__':
    unittest.main()
