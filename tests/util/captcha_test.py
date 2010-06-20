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

from tests.util.compat import EnvironmentStub
from tests.util.trac_test import TracTest
from trac_captcha.controller import TracCaptchaController

class CaptchaTest(TracTest):
    def setUp(self):
        self.super()
        self.enable_ticket_subsystem()
        self.enable_captcha_infrastructure()
        self.env = EnvironmentStub(enable=('trac.*', 'trac_captcha.*',))
        self.disable_component('trac.versioncontrol.api.repositorymanager')
    
    def enable_captcha_infrastructure(self):
        # ensure that all Components are loaded and can be found by trac
        import trac_captcha
    
    def assert_captcha_is_active(self, captcha):
        self.assert_equals(captcha(self.env), TracCaptchaController(self.env).captcha)
    
    def enable_captcha(self, captcha_class):
        class_name = str(captcha_class.__name__)
        self.env.config.set('trac-captcha', 'captcha', class_name)
        fully_qualified_class_name = captcha_class.__module__ + "." + class_name
        self.env.config.set('components', fully_qualified_class_name, 'enabled')
        self.assert_captcha_is_active(captcha_class)

