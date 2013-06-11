import unittest
from time import sleep

from nekhbet import PerfFilter
from nekhbet.perffilter import StatManager

from Queue import Empty

class TestPerformance(unittest.TestCase):

    def setUp(self):
        StatManager.time = 2
        StatManager.do_send = False

    def tearDown(self):
        # set  loop to false
        StatManager.get_manager().loop = False

    def test_perf(self):
        pfilter = PerfFilter(FakeApp)
        environ = FakeEnviron()
        environ.set('PATH_INFO', '/test')
        environ.set('HTTP_ACCEPT', 'text/html')
        pfilter.calculate(environ, None)
        try:
            test = StatManager.get_manager().speed.get(block=False)
            assert(test is not None)
        except Empty:
            self.fail()
        try:
            test = StatManager.get_manager().status.get(block=False)
            assert(test is not None)
        except Empty:
            self.fail()
        pfilter.set_profiler_packages({
            'nekhbet': 'mobyle.web, nekhbet, mobyle.lib',
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

    def set(self, key, value):
        self.environ[key] = value

    def get(self, key):
        if key in self.environ:
            return self.environ[key]
        else:
            return None

