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
from trac.config import ExtensionOption
from trac.core import Component, implements
from trac.perm import IPermissionRequestor

from trac_captcha.api import CaptchaFailedError, ICaptcha

__all__ = ['TracCaptchaController']


class TracCaptchaController(Component):
    
    implements(IPermissionRequestor)
    
    captcha = ExtensionOption('trac-captcha', 'captcha', ICaptcha,
                              'reCAPTCHAImplementation',
        '''Name of the component implementing `ICaptcha`, which is used to 
        generate actual captchas.''')
    
    def should_skip_captcha(self, req):
        return 'CAPTCHA_SKIP' in req.perm
    
    def genshi_stream(self, req):
        if not hasattr(req, 'captcha_data'):
            req.captcha_data = dict()
        return HTML(self.captcha.genshi_stream(req))
    
    def check_captcha_solution(self, req):
        if self.should_skip_captcha(req):
            return None
        try:
            self.captcha.assert_captcha_completed(req)
        except CaptchaFailedError, e:
            req.captcha_data = e.captcha_data
            return e.msg
        return None
    
    # IPermissionRequestor
    def get_permission_actions(self):
        return ['CAPTCHA_SKIP', ('TICKET_ADMIN', ['CAPTCHA_SKIP'])]



