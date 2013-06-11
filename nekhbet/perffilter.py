"""WSGI Request performance tracking

.. moduleauthor:: Olivier Sallou <olivier.sallou@irisa.fr>

"""

from datetime import datetime
import cProfile
import pstats
import io
import threading
#from .consumer import listen_messages
import json
import time
import logging
from Queue import Queue, Empty
log = logging.getLogger(__name__)


"""
Question:
- profiler behavior on multi-thread ?
- one statmngr per filter thread/worker with gunicorn?
 - attache thread profiler to statmanager thread and add stats objects?
"""


class StatManager(object):

    mngr = None
    t1 = None
    time = 30

    do_send = True

    def __init__(self):
        log.warn("Start new stat manager thread")
        self.loop = True
        self.status = Queue(0)
        self.speed = Queue(0)
        self.profiler = None

    @classmethod
    def get_manager(klass):
        if StatManager.mngr is None:
            StatManager.mngr = StatManager()
            StatManager.t1 = threading.Thread(target=StatManager.mngr.send_stats, args=[])
            StatManager.t1.start()
        return StatManager.mngr

    def send_stats(self):
        log.info("Start new thread")
        init = datetime.now()
        last_status = None
        last_speed = None
        while self.loop:
            log.info("new message cycle")
            time.sleep(StatManager.time)
            init = datetime.now()
            if StatManager.do_send:
                # loop through queue to concat data and send stats
                too_recent = False
                status_msg = []
                while not too_recent:
                    if last_status is not None and last_status['time'] < init:
                            status_msg.append(last_status)
                    try:
                        last_status = self.status.get(block=False)
                        log.error(str(last_status))
                        if last_status['time'] >= init:
                            too_recent = True
                        else:
                            status_msg.append(last_status)
                            last_status = None
                    except Empty:
                        too_recent = True

                too_recent = False
                speed_msg = []
                while not too_recent:
                    if last_speed is not None and last_speed['time'] < init:
                            speed_msg.append(last_speed)
                    try:
                        last_speed = self.speed.get(block=False)
                        log.error(str(last_speed))
                        if last_speed['time'] >= init:
                            too_recent = True
                        else:
                            speed_msg.append(last_speed)
                            last_speed = None
                    except Empty:
                        too_recent = True

                log.error("SHOULD AGGREGATE DATA")
                log.info("send new data " + str(init))
                log.info("aggregate and send data " + str(status_msg))
                log.info("aggregate and send data " + str(speed_msg))
            else:
                log.debug("No message sent")


class PerfFilter(object):
    '''
    Performance request counter
    '''
    def __init__(self, app, config=None):
        self.config = config
        print "Load Nekhbet performance filter"
        self.app = app

        self.mystats = {}
        self.mypackages = {}
        if self.config is not None and 'groups' in self.config:
            packages = self.config['groups'].split(',')
        else:
            packages = []
        mytmppackages = {}
        for package in packages:
            pack = package.strip()
            if pack + ".packages" in self.config:
                mytmppackages[pack] = self.config[pack + ".packages"]
        self.set_profiler_packages(mytmppackages)

        #self.profiler = cProfile.Profile()
        self.statmngr = StatManager.get_manager()
        # TODO Should do locking
        if self.statmngr.profiler is None:
            self.statmngr.profiler = cProfile.Profile()
        self.start_profiling()

        #self.middleware = ProfileMiddleware(
        #       self.app,
        #       log_filename='nekhbet.log',
        #       cachegrind_filename='cachegrind.out.nekhbet',
        #       discard_first_request=True,
        #       flush_at_shutdown=True,
        #       path='/__profile__',
        #       unwind=False,
        #      )

    def set_profiler_packages(self, packages):
        '''
        Define packages to group for statistics
        :param packages: dict of package
        :type packages: dict
        '''
        self.mypackages = packages
        for package in packages:
            self.mystats[package] = 0

    def start_profiling(self):
        self.statmngr.profiler.enable()

    def stop_profiling(self):
        self.statmngr.profiler.disable()

    def get_profiling(self):
        s = io.StringIO()
        ps = pstats.Stats(self.statmngr.profiler, stream=s)
        ps.dump_stats('prof.out')

    def profiler_stats(self):
        '''
        get profiling per selected package
        '''
        s = io.StringIO()
        ps = pstats.Stats(self.statmngr.profiler, stream=s)
        stat_list = ps.stats.keys()
        for key in stat_list:
            (pfile, pline, pmethod) = key
            (cc, nc, tt, ct, callers) = ps.stats[key]
            if pfile == '~':
                parentfile = ''
                for parent in callers.keys():
                    (parentfile, parentline, parentmethod) = parent
                    break
                self.profiler_compute(parentfile, tt)
            else:
                self.profiler_compute(pfile, tt)
        return self.mystats

    def profiler_compute(self, pfile, totaltime):
        '''
        Add total time according to packages configuration
        '''
        for package in self.mypackages:
            modules = self.mypackages[package].split(',')
            modules = sorted(modules, key=lambda x: len(x.split('.')),
                            reverse=True)
            for module in modules:
                mpath = module.replace('.', '/').strip()
                if pfile.find(mpath) > -1:
                    self.mystats[package] += totaltime
                    break

    def calculate(self, environ, start_response):
        '''
        Calculate time elapsed for a request URL
        '''
        if str(environ.get('PATH_INFO')) == "/__profile__":
            status = '200 OK'
            response_headers = [('Content-Type', 'application/json')]
            start_response(status, response_headers)
            stats = self.profiler_stats()
            status = {'status': self.statmngr.status,
                        'speed': self.statmngr.speed, 'stats': stats}
            # TODO, remove later, this is for debug
            self.get_profiling()
            return json.dumps(status)
        # Track URL
        #print "URL " + str(environ.get('PATH_INFO'))
        url = environ.get('PATH_INFO')
        before = datetime.now()

        def _start_response(status, headers, *args):
            '''
            Intermediate filter to track response headers
            and status
            '''
            if environ.get("HTTP_ACCEPT").find('text/html') < 0:
                return start_response(status, headers, *args)
            self.statmngr.status.put({url: status, 'time': datetime.now()})
            return start_response(status, headers, *args)

        res = self.app(environ, _start_response)
        after = datetime.now()
        # Track response time
        elapsed = (after - before).total_seconds()
        if environ.get("HTTP_ACCEPT").find('text/html') >= 0:
            self.statmngr.speed.put({url: elapsed, 'time': datetime.now()})
        #self.get_profiling()
        return res

    def __call__(self, environ, start_response):
        return self.calculate(environ, start_response)
