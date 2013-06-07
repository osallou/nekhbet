# -*- coding: utf-8 -*-
from hashlib import sha1
from random import randint

from pyramid.config import Configurator

from pyramid.events import subscriber
from pyramid.events import NewRequest, BeforeRender, NewResponse
from pyramid.security import authenticated_userid
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
import pyramid_beaker



def main(global_config, **settings):
    """ 
    This function returns a Pyramid WSGI application.
    """

    # Mobyle modules (which import mobyle.lib modules) can be imported
    # now, they are registered with the right configuration
    from nekhbet.web.resources import Root

    config = Configurator(root_factory = Root, settings = settings)
    config.include(pyramid_beaker)
    config.include('pyramid_mailer')
    
    config.add_route('main', '/')

    config.add_static_view('static', 'nekhbet.web:static', cache_max_age = 3600)
    config.scan()

    return config.make_wsgi_app()
