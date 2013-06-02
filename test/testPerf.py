import unittest
from datetime import datetime
import logging

from nekhbet import PerfFilter



class TestPerformance(unittest.TestCase):

  def setUp(self):
    pass

  def test_perf(self):
    pfilter = PerfFilter(FakeApp)
    environ = FakeEnviron()
    environ.set('HTTP_REFERER', '/test')
    pfilter.calculate(environ, None)
    assert(len(pfilter.counters)==1)


class FakeApp(object):

    def __init__(self, environ, response):
        self.environ = environ

class FakeEnviron:

    def __init__(self):
        self.environ = {}

    def set(self,key,value):
        self.environ[key] = value

    def get(self,key):
        return self.environ[key]

