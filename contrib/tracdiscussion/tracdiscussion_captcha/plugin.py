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

from genshi.filters.transform import Transformer
from trac.core import Component, implements
from trac.web.api import ITemplateStreamFilter

from trac_captcha.controller import TracCaptchaController

from tracdiscussion.api import IDiscussionFilter


class TracDiscussionCaptcha(Component):
    
    implements(ITemplateStreamFilter, IDiscussionFilter)
    
    # --- IDiscussionFilter ----------------------------------------------------
    
    def filter_topic(self, context, topic):
        return self.reject_if_captcha_not_solved(context.req, topic)
    
    def filter_message(self, context, message):
        return self.reject_if_captcha_not_solved(context.req, message)
    
    
    # --- ITemplateStreamFilter ------------------------------------------------
    
    def filter_stream(self, req, method, filename, stream, data):
        if filename not in ('topic-add.html', 'message-list.html'):
            return stream
        transformer = Transformer('//div[@class="buttons"]')
        return TracCaptchaController(self.env).inject_captcha_into_stream(req, stream, transformer)
    
    # --- private API ----------------------------------------------------------
    def reject_if_captcha_not_solved(self, req, submission):
        error_message = TracCaptchaController(self.env).check_captcha_solution(req)
        if error_message is None:
            return (True, submission)
        return (False, error_message)

