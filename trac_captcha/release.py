# -*- coding: UTF-8 -*-

name = 'TracCaptcha'
version = '0.1'
description = 'pluggable captcha infrastructure for trac with reCAPTCHA included'
long_description = '''
TracCaptcha is a set of trac plugins to embed captchas in addition to Trac's 
regular permission checks so that spammers are kept out.

Generic Infrastructure: TracCaptcha takes care about embedding a
given captcha in the appropriate places which means that building a different 
captcha plugin is easy - you just have to build the captcha itself while this
code will take care of the trac integration.

Flexible Permissions: You can configure that the captcha is not displayed for 
certain users or groups (e.g. 'all authenticated users') just by using Trac's
permission system.

Batteries included: The popular reCAPTCHA system is supported out of the box.
Technically it's a plugin - if you don't like it you're free to use any other 
plugin while still leverage the benefits from the general captcha 
infrastructure.


Changelog
******************************

0.1
==================
 - initial release: you can protect ticket pages with reCAPTCHA
'''
author = 'Felix Schwarz'
email = 'felix.schwarz@oss.schwarz.eu'
url = 'http://www.schwarz.eu/opensource/projects/trac_captcha'
download_url = 'http://www.schwarz.eu/opensource/projects/%(name)s/download/%(version)s/%(name)s-%(version)s.tar.gz' % dict(name=name, version=version)
copyright = u'2010 Felix Schwarz'
license='MIT'

