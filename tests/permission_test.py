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

from trac_captcha.lib.version import Version
from trac_captcha.test_util import CaptchaTest
from trac_captcha.trac_version import trac_version

class CaptchaPermissionTest(CaptchaTest):
    
    def test_has_action_to_skip_captcha(self):
        self.assert_has_no_permission('anonymous', 'CAPTCHA_SKIP')
        
        self.grant_permission('anonymous', 'CAPTCHA_SKIP')
        self.assert_has_permission('anonymous', 'CAPTCHA_SKIP')
    
    def test_ticket_admin_has_implicit_permission_to_skip_captcha(self):
        # functionality is only available with Trac 0.13 (Trac's r10417), 
        # see http://trac.edgewall.org/ticket/8036
        # skip this test otherwise
        if trac_version < Version(major=0, minor=13):
            return
        self.assert_has_no_permission('foo', 'CAPTCHA_SKIP')
        
        self.grant_permission('foo', 'TICKET_ADMIN')
        self.assert_has_permission('foo', 'CAPTCHA_SKIP')
    
    def test_ticket_admin_keeps_other_permissions(self):
        self.assert_has_no_permission('anonymous', 'TICKET_CREATE')
        
        self.grant_permission('anonymous', 'TICKET_ADMIN')
        self.assert_has_permission('anonymous', 'TICKET_CREATE')
        

