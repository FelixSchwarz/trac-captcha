#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

import setuptools

from trac_captcha.lib.distribution_helpers import information_from_file


def add_simplejson_if_necessary(a_list_or_dict):
    try:
        import json
    except ImportError:
        if hasattr(a_list_or_dict, 'append'):
            a_list_or_dict.append('simplejson')
        else:
            a_list_or_dict['simplejson'] = ['simplejson']

tests_require = []
add_simplejson_if_necessary(tests_require)

extras_require = {'Babel': ['Babel']}
add_simplejson_if_necessary(extras_require)

release_filename = os.path.join('trac_captcha', 'release.py')
externally_defined_parameters= information_from_file(release_filename)

setuptools.setup(
    install_requires=['genshi', 'trac >= 0.11'],
    extras_require=extras_require,
    tests_require=['nose', 'BeautifulSoup', 'Babel'] + tests_require,
    
    # simple_super is not zip_safe
    zip_safe=False,
    packages=setuptools.find_packages(exclude=['tests']),
    classifiers = (
            'Development Status :: 4 - Beta',
            'Framework :: Trac',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries :: Python Modules',
    ),
    entry_points = {
        'trac.plugins': [
            'trac_captcha = trac_captcha',
            'trac_recaptcha = trac_recaptcha',
        ]
    },
    test_suite = 'nose.collector',
    **externally_defined_parameters
)


