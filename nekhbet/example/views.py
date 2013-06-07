# -*- coding: utf-8 -*-
from pyramid.view import view_config
from pyramid.security import remember, authenticated_userid, forget
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPForbidden
from pyramid.renderers import render_to_response
from pyramid.response import Response

import json
import requests

import logging
log = logging.getLogger(__name__)

@view_config(route_name='main', renderer='mobyle.web:templates/index.mako')
def main_page(request):
    return {'project':'nekhbet' }

