#!/usr/bin/env python

from setuptools import setup, find_packages

requires = [ "pymongo", "repoze.profile", "pika", 'pyramid>=1.4',
    'pyramid_debugtoolbar',
    'waitress',
    'pyramid_beaker',
    ]

setup(name='nekhbet',
      version='0.1.0',
      description='WSGI middleware filter to track request performances',
      author='Olivier Sallou',
      author_email='olivier.sallou@irisa.fr',
      license='BSD',
      url='https://github.com/osallou/nekhbet',
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True,
      install_requires=requires,
      tests_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = nekhbet.example:main
      [paste.filter_factory]
      perf_filter_factory=nekhbet:perf_filter_factory
      """,
     )
