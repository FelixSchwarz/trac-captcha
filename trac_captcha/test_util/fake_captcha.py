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

from genshi.builder import tag
from trac.core import Component, implements

from trac_captcha.api import CaptchaFailedError, ICaptcha


__all__ = ['FakeCaptcha']

class FakeCaptcha(Component):
    implements(ICaptcha)
    
    def genshi_stream(self, req):
        return tag.div('fake captcha: ' + req.captcha_data.get('old_input', ''))
    
    def assert_captcha_completed(self, req):
        if req.args.get('fake_captcha') == 'open sesame':
            return
        msg = 'Please fill in the CAPTCHA so we know you are not a spammer.'
        captcha_data = dict(old_input=req.args.get('fake_captcha', ''))
        raise CaptchaFailedError(msg, captcha_data)

