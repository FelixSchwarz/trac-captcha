# -*- coding: UTF-8 -*-

name = 'TracCaptcha'
version = '0.2.1'
description = 'pluggable captcha infrastructure for trac with reCAPTCHA included'
long_description = '''
TracCaptcha is a trac plugin to embed a captcha in the ticket page in addition 
to Trac's regular permission checks so that spammers are kept out.

**"It just works":** Installation and configuration is very simple, just 
install the egg and put two configuration options in your trac.ini. No 
database changes required.

**Batteries included:** The popular reCAPTCHA system is supported out of the box.
Technically it's a plugin - if you don't like it you're free to use any other 
plugin while still leverage the benefits from the general captcha 
infrastructure.

**Does not annoy users:** After the user entered the captcha once, he does not have
to solve the captcha again for the same ticket when he just clicks 'preview'.
Also you can configure exempt certain users or groups (e.g. 'all authenticated 
users') from the captchas just by using Trac's permission system.

**Easy to extend:** Protecting an additional page with a captcha is very 
simple. Implementing captchas for the ticket module took only 20 lines of code! 
Captchas for the DiscussionPlugin needed 21 lines of code!

**Easy to write custom captchas:** If you don't like reCAPTCHA, you can still 
use the generic infrastructure with all its features: You implement the code to 
generate the captcha and validate the user's input. TracCaptcha will take care 
of displaying your plugin in all supported pages!


Changelog
******************************

0.2.1 (10.11.2010)
====================
- fix "installation" as egg file in Trac plugins folder

0.2 (10.07.2010)
====================
- integration in 3rd party trac plugins: TracDiscussionPlugin and 
  AccountManager (registration only)
- reCAPTCHA: select widget theme via trac.ini (requires simplejson for 
  Python 2.3-2.5)
- reCAPTCHA: display the widget in the user's locale (if translation is provided
  by the reCAPTCHA service)
- reCAPTCHA: use HTTPS to include script files if trac page was served with 
  HTTPS
- reCAPTCHA: show link for reCAPTCHA signup if no keys configured
- reCAPTCHA: use new Google URLs

0.1 (25.06.2010)
==================
 - initial release
'''
author = 'Felix Schwarz'
author_email = 'felix.schwarz@oss.schwarz.eu'
url = 'http://www.schwarz.eu/opensource/projects/trac_captcha'
download_url = 'http://www.schwarz.eu/opensource/projects/%(name)s/download/%(version)s/%(name)s-%(version)s.tar.gz' % dict(name=name, version=version)
# prefix it with '_' so the symbol is not passed to setuptools.setup()
_copyright = u'2010 Felix Schwarz'
license='MIT'

