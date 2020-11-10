import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(".."))
from src.logger import *


def getLastLines(f, n=4):
    lines = f.readlines()
    return lines[-n:]


class LoggerTest(unittest.TestCase):
    def setUp(self):
        self.logger = ClassicLogger(name="test", to_file=True, to_dir="./log", level=logging.DEBUG)

    def tearDown(self):
        pass

    def testDebug(self):
        self.logger.debug(msg="Hello, DEBUG")
        self.logger.info(msg="Hello, INFO")
        self.logger.warn(msg="Hello, WARN")
        # self.logger.error(msg="Hello, ERROR")
        f = open("./log/test.log", "r", encoding="UTF-8")
        logs = getLastLines(f, 3)
        f.close()
        for i, text in enumerate(["DEBUG", "INFO", "WARN"]):
            self.assertGreaterEqual(logs[i].find("Hello, {}".format(text)), 0)

if __name__ == '__main__':
    unittest.main()
