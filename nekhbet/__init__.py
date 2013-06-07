"""WSGI Request performance tracking

.. moduleauthor:: Olivier Sallou <olivier.sallou@irisa.fr>

"""

from datetime import datetime
from .perffilter import PerfFilter

def perf_filter_factory(global_conf, **app_conf):
    '''WSGI filter entry point'''

    if app_conf:
        config = app_conf
    else:
        config = None
        print "No conf"

    def filter(app):
        return PerfFilter(app, config)
    return filter


