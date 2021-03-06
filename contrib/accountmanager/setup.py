#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import setuptools


setuptools.setup(
    name='AccountManagerCaptcha',
    version='0.1',
    
    description='Add captchas for the AccountManager plugin ',
    author='Felix Schwarz',
    author_email='felix.schwarz@oss.schwarz.eu',
    url='http://www.schwarz.eu/opensource/projects/trac_captcha',
    license='MIT',
    
    install_requires=['TracCaptcha > 0.1', 'TracAccountManager'],
    
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
            'captcha = accountmanager_captcha.registration',
        ]
    },
    test_suite = 'nose.collector',
)


