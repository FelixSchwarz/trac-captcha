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

from trac_captcha.lib.testcase import PythonicTestCase
from trac_captcha.test_util.trac_test import MockResponse


class MockResponseTest(PythonicTestCase):
    
    def setUp(self):
        self.super()
        self.response = MockResponse()
    
    def set_body(self, body):
        self.response.body.write(body)
        self.response.body.seek(0)
    
    def test_can_extract_a_single_warning_from_html(self):
        fixture = '''
            <div id="warning" class="system-message">
                <strong>Warning:</strong>
                A warning.
            </div>'''
        self.set_body(fixture)
        self.assert_equals(['A warning.'], self.response.trac_warnings())
    
    def test_can_extract_all_warnings_from_html(self):
        fixture = '''
            <div id="warning" class="system-message">
                <strong>Warning:</strong>
                <ul>
                    <li>first</li>
                    <li>second</li>
                </ul>
            </div>'''
        self.set_body(fixture)
        self.assert_equals(['first', 'second'], self.response.trac_warnings())
    
    def test_does_not_fail_if_no_warnings_are_present(self):
        self.set_body('')
        self.assert_equals([], self.response.trac_warnings())
    
    def test_can_extract_http_status_code(self):
        self.response.status_line = '200 Ok'
        self.assert_equals(200, self.response.code())

