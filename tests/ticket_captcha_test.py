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

from trac.ticket import Ticket

from tests.util.captcha_test import CaptchaTest
from tests.util.fake_captcha import FakeCaptcha


class TicketCaptchaTest(CaptchaTest):
    
    def setUp(self):
        self.super()
        self.enable_captcha(FakeCaptcha)
        self.grant_permission('anonymous', 'TICKET_CREATE')
        self.grant_permission('anonymous', 'TICKET_VIEW')
    
    def assert_number_of_tickets(self, nr_tickets):
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute('SELECT count(*) from ticket')
        nr_rows = (list(cursor)[0])[0]
        self.assert_equals(nr_tickets, nr_rows)
    
    def test_can_insert_captcha_when_creating_a_new_ticket(self):
        response = self.simulate_request(self.request('/newticket', method='GET'))
        self.assert_equals([], response.trac_warnings())
        self.assert_equals(200, response.code())
        self.assert_contains('fake captcha', response.body.read())
    
    def test_can_create_a_ticket_if_captcha_was_entered_correctly(self):
        req = self.post_request('/newticket', field_summary='Foo', 
                                fake_captcha='open sesame')
        response = self.simulate_request(req)
        self.assert_equals(303, response.code())
        self.assert_number_of_tickets(1)
    
    def test_reject_ticket_submission_if_captcha_not_entered_at_all(self):
        req = self.post_request('/newticket', field_summary='Foo')
        response = self.simulate_request(req)
        self.assert_equals(200, response.code())
        self.assert_equals(['Please fill in the CAPTCHA so we know you are not a spammer.'], 
                           response.trac_warnings())
        self.assert_number_of_tickets(0)

