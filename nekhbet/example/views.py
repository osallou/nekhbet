# -*- coding: utf-8 -*-
from pyramid.view import view_config
import time

import logging
log = logging.getLogger(__name__)


@view_config(route_name='main', renderer='nekhbet.example:templates/index.mako')
def main_page(request):
    time.sleep(2)
    return {'project': 'nekhbet'}

