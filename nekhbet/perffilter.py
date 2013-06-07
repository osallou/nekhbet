"""WSGI Request performance tracking

.. moduleauthor:: Olivier Sallou <olivier.sallou@irisa.fr>

"""

from datetime import datetime
import cProfile, pstats, io
import threading
from .consumer import listen_messages

class PerfFilter(object):
    '''
    Performance request counter
    '''
    def __init__(self, app, config=None):
        self.config = config
        print "Load Nekhbet performance filter"
        self.app = app
        self.counters = {}

        self.mystats = { }
        self.mypackages = { }

        self.profiler = cProfile.Profile()
        if self.config and not self.config['standalone']:
            t1 = threading.Thread(target=listen_messages, args=[])
            t1.start()
        else:
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

    def start_profiling(self):
        self.profiler.enable()

    def stop_profiling(self):
        self.profiler.disable()

    def get_profiling(self):
        s = io.StringIO()
        ps = pstats.Stats(self.profiler,stream=s)
        ps.dump_stats('prof.out')

    def profiler_stats(self):
        '''
        get profiling per selected package
        '''
        s = io.StringIO()
        ps = pstats.Stats(self.profiler,stream=s)
        stat_list = ps.stats.keys()
        for key in stat_list:
            (pfile, pline, pmethod) = key
            (cc, nc, tt, ct, callers) = ps.stats[key]
            if pfile =='~':
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
            modules = sorted(modules, key=lambda x: len(x.split('.')), reverse=True)
            for module in modules:
                mpath = module.replace('.','/').strip()
                if pfile.find(mpath) > -1:
                    self.mystats[package] += totaltime
                    break

    def calculate(self, environ, start_response):
        '''
        Calculate time elapsed for a request URL
        '''
        # Track URL
        print "URL "+str(environ.get('HTTP_REFERER'))
        before = datetime.now()

        def _start_response(status, headers, *args):
            '''
            Intermediate filter to track response headers
            and status
            '''
            # Should track only html content/type,
            # not static ones such css, img...
            print "STATUS: "+status
            print "HEADERS: "+str(headers)
            return start_response(status, headers, *args)

        res = self.app(environ, _start_response)
        after = datetime.now()
        # Track response time
        elapsed = (after - before).total_seconds()
        self.counters[before] = elapsed
        print "elapsed "+str(elapsed)
        self.get_profiling()
        return res

    def __call__(self, environ, start_response):
        return self.calculate(environ, start_response)

