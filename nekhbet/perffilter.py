"""WSGI Request performance tracking

.. moduleauthor:: Olivier Sallou <olivier.sallou@irisa.fr>

"""

from datetime import datetime
from repoze.profile import ProfileMiddleware

class PerfFilter(object):
    '''
    Performance request counter
    '''
    def __init__(self, app):
        print "Load Nekhbet performance filter"
        self.app = app
        self.counters = {}

        #self.middleware = ProfileMiddleware(
        #       self.app,
        #       log_filename='nekhbet.log',
        #       cachegrind_filename='cachegrind.out.nekhbet',
        #       discard_first_request=True,
        #       flush_at_shutdown=True,
        #       path='/__profile__',
        #       unwind=False,
        #      )

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
        return res

    def __call__(self, environ, start_response):
        return self.calculate(environ, start_response)

