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

import urlparse

from genshi.builder import tag
from trac.config import BoolOption, Option
from trac.core import Component, implements
from trac.web.href import Href

from trac_captcha.api import ICaptcha
from trac_captcha.controller import TracCaptchaController
from trac_captcha.i18n import _
from trac_recaptcha.client import reCAPTCHAClient, is_empty
from trac_recaptcha.genshi_widget import GenshiReCAPTCHAWidget

__all__ = ['reCAPTCHAImplementation']


def trac_hostname(req):
    def host_from_base_url():
        base_url = req.environ.get('trac.base_url')
        if base_url is None:
            return None
        return urlparse.urlsplit(base_url)[1]
    
    for collector in (host_from_base_url, lambda: req.get_header('host'), 
                      lambda: req.environ.get('SERVER_NAME')):
        hostname = collector()
        if hostname is not None:
            return hostname
    raise AssertionError('No hostname found!')


class reCAPTCHAImplementation(Component):
    implements(ICaptcha)
    
    public_key = Option('recaptcha', 'public_key')
    private_key = Option('recaptcha', 'private_key')
    theme = Option('recaptcha', 'theme')
    require_javascript = BoolOption('recaptcha', 'require_javascript', False)
    
    # --- ICaptcha -------------------------------------------------------------
    def genshi_stream(self, req):
        error_xml = self.warn_if_private_key_or_public_key_not_set(req)
        if error_xml is not None:
            return error_xml
        use_https = req.scheme == 'https'
        error_code = self.error_code_from_request(req)
        widget = GenshiReCAPTCHAWidget(self.public_key, use_https=use_https, 
                                       error=error_code, js_config=self.js_config(req), 
                                       log=self.env.log, noscript=not self.require_javascript)
        return widget.xml()
    
    def assert_captcha_completed(self, req, client_class=None):
        client = self.client(client_class)
        remote_ip = req.remote_addr
        challenge = req.args.get('recaptcha_challenge_field')
        response = req.args.get('recaptcha_response_field')
        client.verify(remote_ip, challenge, response)
        
        controller = TracCaptchaController(self.env)
        base_message = 'Captcha for %(path)s successfully solved with %(challenge)s/%(response)s and %(arguments)s'
        parameters = dict(path=req.path_info, challenge=repr(challenge), response=repr(response), arguments=repr(req.args))
        controller.debug_log(base_message % parameters)
        
    
    # --- private --------------------------------------------------------------
    
    def client(self, client_class):
        client_class = client_class and client_class or reCAPTCHAClient
        return client_class(self.private_key)
    
    def error_code_from_request(self, req):
        if hasattr(req, 'captcha_data'):
            return req.captcha_data.get('error_code')
        return None
    
    def warn_if_private_key_or_public_key_not_set(self, req):
        if is_empty(self.public_key):
            url_base = Href('http://www.google.com/recaptcha/admin')
            link = tag.a(_(u'sign up for a reCAPTCHA now'), 
                         href=url_base(app='TracCaptcha', domain=trac_hostname(req)))
            return tag.div(
                _(u'No public key for reCAPTCHA configured. Please add your '
                  u'reCAPTCHA key to your trac.ini ([recaptcha]/public_key). '),
                
                # TRANSLATOR: "If you don't have a key, you can sign up for ... ."
                _('If you don\'t have a key, you can '), link, _('.')
            )
        
        return None
    
    def js_config(self, req):
        config = dict()
        if getattr(req, 'locale', None) is not None:
            # For trac 0.12 without Babel installed, req.locale is None
            config['lang'] = req.locale.language
        if self.theme:
            config['theme'] = self.theme
        return config or None

