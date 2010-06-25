# -*- coding: UTF-8 -*-

name = 'TracCaptcha'
version = '0.1'
description = 'pluggable captcha infrastructure for trac with reCAPTCHA included'
long_description = '''
TracCaptcha is a trac plugin to embed a captcha in the ticket page in addition 
to Trac's regular permission checks so that spammers are kept out.

Batteries included: The popular reCAPTCHA system is supported out of the box.
Technically it's a plugin - if you don't like it you're free to use any other 
plugin while still leverage the benefits from the general captcha 
infrastructure.

Does not annoy users: After the user entered the captcha once, he does not have
to solve the captcha again for the same ticket when he just clicks 'preview'.
Also you can configure exempt certain users or groups (e.g. 'all authenticated 
users') from the captchas just by using Trac's permission system.

Generic Infrastructure: TracCaptcha takes care about embedding a
given captcha in the appropriate places which means that building a different 
captcha plugin is easy - you just have to build the captcha itself while this
code will take care of the trac integration.


Changelog
******************************

0.1 (25.06.2010)
==================
 - initial release
'''
author = 'Felix Schwarz'
email = 'felix.schwarz@oss.schwarz.eu'
url = 'http://www.schwarz.eu/opensource/projects/trac_captcha'
download_url = 'http://www.schwarz.eu/opensource/projects/%(name)s/download/%(version)s/%(name)s-%(version)s.tar.gz' % dict(name=name, version=version)
copyright = u'2010 Felix Schwarz'
license='MIT'

