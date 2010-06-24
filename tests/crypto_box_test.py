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

from datetime import datetime, timedelta

from trac.util.datefmt import localtz

from trac_captcha.cryptobox import CryptoBox
from trac_captcha.lib.testcase import PythonicTestCase


class CryptBoxTest(PythonicTestCase):
    def setUp(self):
        self.box = CryptoBox('foobar')
    
    def raw_token(self, message):
        return message + '||' + self.box.sign_message(message)
    
    def token(self, valid_until=None):
        return self.raw_token(self.box.token_payload(valid_until=valid_until))
    
    def assert_invalid(self, token):
        self.assert_false(self.box.is_token_valid(token), token)
    
    def assert_valid(self, message):
        token = self.raw_token(message)
        self.assert_true(self.box.is_token_valid(token), token)
    
    
    def test_knows_if_token_is_valid(self):
        self.assert_valid(self.box.token_payload())
    
    def test_can_detect_invalid_token_syntax(self):
        self.assert_invalid('foo')
        self.assert_invalid(None)
        self.assert_invalid(['foo'])
        self.assert_invalid(self.token() + '||bar')
        self.assert_invalid(self.token().replace('||', '--'))
        self.assert_invalid(self.raw_token('foo'))
    
    def test_can_detect_invalid_token_hash(self):
        self.assert_invalid(self.box.token_payload() + '||' + self.box.sign_message('bar'))
    
    def test_can_detect_expired_tokens(self):
        yesterday = datetime.now(localtz) - timedelta(days=1)
        self.assert_invalid(self.token(valid_until=yesterday))
    
    def test_can_generate_valid_tokens(self):
        self.assert_true(self.box.is_token_valid(self.box.generate_token()))


