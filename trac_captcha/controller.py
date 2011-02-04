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

from genshi import HTML
from genshi.builder import tag
import pkg_resources
from trac.config import ExtensionOption, Option
from trac.core import Component, implements
from trac.perm import IPermissionRequestor

from trac_captcha.api import CaptchaFailedError, ICaptcha
from trac_captcha.cryptobox import CryptoBox
from trac_captcha.i18n import add_domain
from trac_captcha.lib.version import Version
from trac_captcha.trac_version import trac_version

__all__ = ['initialize_captcha_data', 'TracCaptchaController']


def initialize_captcha_data(req):
    if not hasattr(req, 'captcha_data'):
        req.captcha_data = dict()

class TracCaptchaController(Component):
    
    implements(IPermissionRequestor)
    
    captcha = ExtensionOption('trac-captcha', 'captcha', ICaptcha,
                              'reCAPTCHAImplementation',
        '''Name of the component implementing `ICaptcha`, which is used to 
        generate actual captchas.''')
    
    stored_token_key = Option('trac-captcha', 'token_key',  None, 
        '''Generated private key which is used to encrypt captcha tokens.''')
    
    def __init__(self):
        super(TracCaptchaController, self).__init__()
        locale_dir = pkg_resources.resource_filename(__name__, 'locale')
        add_domain(self.env.path, locale_dir)
    
    # --- IPermissionRequestor -------------------------------------------------
    def get_permission_actions(self):
        permissions = ['CAPTCHA_SKIP']
        if Version(major=0, minor=13) <= trac_version:
            # enhancing existing meta-permissions is only possible since 
            # Trac's r10417 (which is in 0.13), see
            # http://trac.edgewall.org/ticket/8036
            permissions.append(('TICKET_ADMIN', ['CAPTCHA_SKIP']))
        return permissions
    
    # --- public API -----------------------------------------------------------
    def should_skip_captcha(self, req):
        if 'CAPTCHA_SKIP' in req.perm:
            return True
        captcha_token = req.args.get('__captcha_token')
        if self.is_token_valid(captcha_token):
            self.add_token_for_request(req, captcha_token)
            return True
        return False
    
    def check_captcha_solution(self, req):
        if self.should_skip_captcha(req):
            return None
        try:
            self.captcha.assert_captcha_completed(req)
        except CaptchaFailedError, e:
            req.captcha_data = e.captcha_data
            return e.msg
        self.add_token_for_request(req)
        return None
    
    # Captcha generation / Genshi stream manipulation
    def captcha_html(self, req):
        return HTML(self.captcha.genshi_stream(req))
    
    def inject_captcha_into_stream(self, req, stream, transformer):
        initialize_captcha_data(req)
        if 'token' in req.captcha_data:
            return stream | transformer.before(self.captcha_token_tag(req))
        if self.should_skip_captcha(req):
            return stream
        
        return stream | transformer.before(self.captcha_html(req))
    
    def captcha_token_tag(self, req):
        token = req.captcha_data['token']
        return tag.input(type='hidden', name='__captcha_token', value=token)
    
    # --- private API ----------------------------------------------------------
    
    def add_token_for_request(self, req, token=None):
        if token is None:
            token = CryptoBox(self.token_key()).generate_token()
        initialize_captcha_data(req)
        req.captcha_data['token'] = token
    
    def token_key(self):
        '''Return the private token key stored in trac.ini. If no such key was
        set, a new one will be generated.'''
        if self.stored_token_key in ('', None):
            new_key = CryptoBox().generate_key()
            self.env.config.set('trac-captcha', 'token_key', new_key)
            self.env.config.save()
        return str(self.stored_token_key)
    
    def is_token_valid(self, a_token):
        return CryptoBox(self.token_key()).is_token_valid(a_token)

