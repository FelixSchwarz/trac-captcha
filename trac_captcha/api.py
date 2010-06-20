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

from trac.core import Interface

__all__ = ['CaptchaFailedError', 'ICaptcha']


class CaptchaFailedError(Exception):
    def __init__(self, msg, captcha_data=None):
        Exception.__init__(self, msg)
        self.msg = msg
        self.captcha_data = captcha_data or dict()


class ICaptcha(Interface):
    """Extension point interface for components that implement a specific 
    captcha."""
    
    def genshi_stream(self):
        "Return a Genshi stream which contains the captcha implementation."
    
    def assert_captcha_completed(self, req):
        """Check the request if the captcha was completed successfully. If the
        captcha is incomplete, a CaptchaFailedError is raised."""

