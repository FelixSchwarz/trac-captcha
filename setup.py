#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

import setuptools

def add_simplejson_if_necessary(a_list):
    try:
        import json
    except ImportError:
        a_list.append('simplejson')

tests_require = []
add_simplejson_if_necessary(tests_require)

extras_require = ['Babel']
add_simplejson_if_necessary(extras_require)

execfile(os.path.join('trac_captcha', 'release.py'))

setuptools.setup(
    name=name,
    version=version,
    
    description=description,
    long_description=long_description,
    author=author,
    author_email=email,
    url=url,
    download_url=download_url,
    license=license,
    
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
)


