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

from trac_captcha.test_util import CaptchaTest
from trac_captcha.controller import TracCaptchaController
from trac_captcha.cryptobox import CryptoBox


class TracCaptchaControllerTest(CaptchaTest):
    
    def setUp(self):
        self.super()
        self.controller = TracCaptchaController(self.env)
        self.assert_false(self.has_permission('anonymous', 'CAPTCHA_SKIP'))
    
    def captcha_token(self):
        return CryptoBox(self.controller.token_key()).generate_token()
    
    
    def test_token_key_from_configuration_always_returned_as_byte_string(self):
        # all crypto algorithms only work on unicode instances, even if they
        # only contain ASCII characters
        self.assert_true(isinstance(self.controller.token_key(), str))
    
    def test_can_generate_token_key_if_not_set(self):
        self.assert_equals('', self.env.config.get('trac-captcha', 'token_key'))
        self.assert_not_none(self.controller.token_key())
        
        stored_token = self.env.config.get('trac-captcha', 'token_key')
        self.assert_equals(self.controller.token_key(), stored_token)
    
    def test_returns_token_key_if_stored_in_config(self):
        self.env.config.set('trac-captcha', 'token_key', 'foobar')
        
        self.assert_equals('foobar', self.controller.token_key())
    
    def test_skip_captcha_if_valid_token_found(self):
        self.env.config.set('trac_captcha', 'token_key', 'foobar')
        req = self.request('/', __captcha_token=self.captcha_token())
        self.assert_none(None, req.remote_user)
        
        self.assert_true(self.controller.should_skip_captcha(req))
    
    def test_ignore_invalid_tokens(self):
        req = self.request('/', __captcha_token='foobar')
        self.assert_none(None, req.remote_user)
        
        self.assert_false(self.controller.should_skip_captcha(req))


