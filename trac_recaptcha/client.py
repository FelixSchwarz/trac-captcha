# -*- coding: UTF-8 -*-
# 
# The MIT License
# 
# Copyright (c) 2010-2011 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from urllib import urlencode
import urllib2

try:
    # try not to depend on trac_captcha so this file can be reused within other
    # software without dependencies on TracCaptcha or Trac.
    from trac_captcha.api import CaptchaFailedError
    from trac_captcha.i18n import _
except ImportError:
    from gettext import gettext as _
    
    class CaptchaFailedError(Exception):
        def __init__(self, msg, captcha_data=None):
            Exception.__init__(self, msg)
            self.msg = msg
            self.captcha_data = captcha_data or dict()


__all__ = ['is_empty', 'reCAPTCHAClient']


def is_string(instance):
    return hasattr(instance, 'strip')

def is_empty(parameter):
    return (not is_string(parameter)) or parameter.strip() == ''


class reCAPTCHAClient(object):
    def __init__(self, private_key):
        self.private_key = private_key
    
    def verify_server(self):
        return 'http://www.google.com/recaptcha/api/verify'
    
    def raise_error(self, error_code, msg=None):
        msg = msg or _(u'Incorrect captcha input - please try again…')
        raise CaptchaFailedError(msg, dict(error_code=error_code))
    
    def raise_server_unreachable_error(self):
        self.raise_error('recaptcha-not-reachable')
    
    def raise_incorrect_solution_error(self, error_code='incorrect-captcha-sol'):
        self.raise_error(error_code)
    
    def ask_verify_server(self, url, parameters):
        def to_utf8(value):
            return hasattr(value, 'encode') and value.encode('utf-8') or value
        utf8_parameters = dict([(key, to_utf8(value)) for key, value in parameters.items()])
        try:
            response = urllib2.urlopen(url, urlencode(utf8_parameters))
            response_content = response.read()
            response.close()
        except IOError:
            self.raise_server_unreachable_error()
        return response_content
    
    def assert_server_accepted_solution(self, response):
        lines = response.splitlines()
        if len(lines) == 0:
            self.raise_server_unreachable_error()
        if lines[0] == 'true':
            return
        if len(lines) < 2:
            self.raise_server_unreachable_error()
        raise self.raise_incorrect_solution_error(lines[1])
    
    def no_input_given(self, challenge, response):
        return is_empty(challenge) or is_empty(response)
    
    def raise_missing_private_key_error(self):
        msg = _(u'Can not verify captcha because the reCAPTCHA private key is '
                u'missing. Please add your reCAPTCHA key to your trac.ini '
                u'([recaptcha] private_key).')
        self.raise_error('invalid-site-private-key', msg=msg)
    
    def verify(self, remote_ip, challenge, response, probe=None):
        if self.no_input_given(challenge, response):
            self.raise_incorrect_solution_error()
        if is_empty(self.private_key):
            self.raise_missing_private_key_error()
        parameters = dict(privatekey=self.private_key, remoteip=remote_ip,
                          challenge=challenge, response=response)
        verify_method = probe and probe or self.ask_verify_server
        response = verify_method(self.verify_server(), parameters)
        self.assert_server_accepted_solution(response)


