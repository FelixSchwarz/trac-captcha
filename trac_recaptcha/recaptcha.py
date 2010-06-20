# -*- coding: UTF-8 -*-
# 
# The MIT License
# 
# Copyright (c) 2010 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
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

from genshi.builder import tag
from trac.config import Option
from trac.core import Component, implements
from trac.util.translation import _

from trac_captcha.api import CaptchaFailedError, ICaptcha

__all__ = ['reCAPTCHAImplementation']

# TODO: Support translations on 0.12
# TODO: Support custom styles
# TODO: Detect SSL sites

class GenshiReCAPTCHAWidget(object):
    def __init__(self, public_key, use_https=False, error=None):
        self.public_key = public_key
        self.use_https = use_https
        self.error = error
    
    def recaptcha_domain(self):
        if self.use_https:
            return 'https://api-secure.recaptcha.net'
        return 'http://api.recaptcha.net'
    
    def challenge_url(self):
        url_path = '%(domain)s/challenge?' % dict(domain=self.recaptcha_domain())
        parameters = dict(k=self.public_key)
        if self.error is not None:
            parameters['error'] = self.error
        return url_path + urlencode(parameters)
    
    def noscript_url(self):
        url_path = '%(domain)s/noscript?' % dict(domain=self.recaptcha_domain())
        parameters = dict(k=self.public_key)
        if self.error is not None:
            parameters['error'] = self.error
        return url_path + urlencode(parameters)
    
    def widget_tag(self):
        return tag.script(src=self.challenge_url(), type='text/javascript')
    
    def noscript_fallback_tag(self):
        return tag.noscript(
            tag.iframe(src=self.noscript_url(), height=300, width=500, frameborder=0),
            tag.br(),
            tag.textarea(name='recaptcha_challenge_field', rows=3, cols=40),
            tag.input(type='hidden', name='recaptcha_response_field', value='manual_challenge'),
        )
    
    def xml(self):
        return tag.span(self.widget_tag(), self.noscript_fallback_tag())


class reCAPTCHAClient(object):
    def __init__(self, private_key):
        self.private_key = private_key
    
    def verify_server(self):
        return 'http://api-verify.recaptcha.net/verify'
    
    def raise_error(self, error_code):
        msg = _(u'Incorrect captcha input - please try again...')
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
        def is_string(instance):
            return hasattr(instance, 'strip')
        def is_empty(parameter):
            return (not is_string(parameter)) or parameter.strip() == ''
        return is_empty(challenge) or is_empty(response)
    
    def verify(self, remote_ip, challenge, response, probe=None):
        if self.no_input_given(challenge, response):
            self.raise_incorrect_solution_error()
        parameters = dict(privatekey=self.private_key, remoteip=remote_ip,
                          challenge=challenge, response=response)
        verify_method = probe and probe or self.ask_verify_server
        response = verify_method(self.verify_server(), parameters)
        self.assert_server_accepted_solution(response)


class reCAPTCHAImplementation(Component):
    implements(ICaptcha)
    
    public_key = Option('recaptcha', 'public_key')
    private_key = Option('recaptcha', 'private_key')
    
    # --- ICaptcha -------------------------------------------------------------
    def genshi_stream(self, req):
        error_code = None
        if hasattr(req, 'captcha_data'):
            error_code = req.captcha_data.get('error_code')
        return GenshiReCAPTCHAWidget(self.public_key, error=error_code).xml()
    
    def assert_captcha_completed(self, req, client_class=None):
        client = self.client(client_class)
        remote_ip = req.remote_addr
        challenge = req.args.get('recaptcha_challenge_field')
        response = req.args.get('recaptcha_response_field')
        client.verify(remote_ip, challenge, response)
    
    # --- private --------------------------------------------------------------
    
    def client(self, client_class):
        client_class = client_class and client_class or reCAPTCHAClient
        return client_class(self.private_key)

