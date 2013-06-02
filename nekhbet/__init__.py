"""WSGI Request performance tracking

.. moduleauthor:: Olivier Sallou <olivier.sallou@irisa.fr>

"""

from datetime import datetime
from .perffilter import PerfFilter

def perf_filter_factory(global_conf, **app_conf):
    '''WSGI filter entry point'''
    def filter(app):
        return PerfFilter(app)
    return filter


