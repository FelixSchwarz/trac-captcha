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
from trac.ticket.api import ITicketManipulator
from trac.web.api import ITemplateStreamFilter

from trac_captcha.controller import TracCaptchaController

__all__ = ['TicketCaptcha']


class TicketCaptcha(Component):
    implements(ITemplateStreamFilter, ITicketManipulator)
    
    # --- ITemplateStreamFilter ------------------------------------------------
    def filter_stream(self, req, method, filename, stream, data):
        if filename != 'ticket.html':
            return stream
        transformer = Transformer('//div[@class="buttons"]')
        return TracCaptchaController(self.env).inject_captcha_into_stream(req, stream, transformer)
    
    # --- ITicketManipulator ---------------------------------------------------
    def prepare_ticket(self, req, ticket, fields, actions):
        pass
    
    def validate_ticket(self, req, ticket):
        error_message = TracCaptchaController(self.env).check_captcha_solution(req)
        if error_message is None:
            return ()
        return ((None, error_message),)
    


