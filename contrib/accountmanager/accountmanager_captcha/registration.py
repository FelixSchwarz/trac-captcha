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

import acct_mgr.web_ui
from genshi.filters.transform import Transformer
from trac.core import Component, implements, TracError
from trac.web.api import ITemplateStreamFilter
from trac.web.chrome import add_warning

from trac_captcha.controller import TracCaptchaController

# AccountManager does not have an interface to veto user registration
# we could implemented IRequestFilter.pre_process_request, but then we need to
# redirect on failed captcha input which does not fit in the current (July 2010)
# TracCaptcha architecture - we'd need to store all parameters in the user's
# session but currently they are only stored in the request data.
original_user_creation = acct_mgr.web_ui._create_user
def captcha_protected_user_creation(req, env, check_permissions=True):
    AccountManagerRegistrationCaptcha(env).validate_registration(req)
    return original_user_creation(req, env, check_permissions)
acct_mgr.web_ui._create_user = captcha_protected_user_creation


class AccountManagerRegistrationCaptcha(Component):
    
    implements(ITemplateStreamFilter)
    
    # --- Fake interface to validate newly registered users...  ----------------
    
    def validate_registration(self, req):
        error_message = TracCaptchaController(self.env).check_captcha_solution(req)
        if error_message is None:
            return
        # AccountManager can not retain the password...
        parameters = dict(username=req.args.get('user'), email=req.args.get('email'))
        error = TracError('')
        error.acctmgr = parameters
        error.message = error_message
        add_warning(req, error_message)
        raise error
    
    # --- ITemplateStreamFilter ------------------------------------------------
    
    def filter_stream(self, req, method, filename, stream, data):
        if filename != 'register.html':
            return stream
        transformer = Transformer('//form[@id="acctmgr_registerform"]/input[@type="submit"]')
        return TracCaptchaController(self.env).inject_captcha_into_stream(req, stream, transformer)
    

