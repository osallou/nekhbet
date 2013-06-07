import unittest
from datetime import datetime
import logging
import io
import pstats
from time import sleep

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
    pfilter.set_profiler_packages({'nekhbet': 'mobyle.web, nekhbet, mobyle.lib',
    'test': 'test'})
    stats = pfilter.profiler_stats()
    assert(stats['test'] > 2)


class FakeApp(object):

    def __init__(self, environ, response):
        self.environ = environ
        sleep(2)

class FakeEnviron:

    def __init__(self):
        self.environ = {}

    def set(self,key,value):
        self.environ[key] = value

    def get(self,key):
        return self.environ[key]

