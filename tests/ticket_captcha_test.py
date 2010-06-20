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
    
    def is_fake_captcha_visible(self, response):
        return 'fake captcha' in response.html()
    
    def assert_fake_captcha_is_visible(self, response):
        self.assert_equals(200, response.code())
        self.assert_true(self.is_fake_captcha_visible(response))
    
    def comments_for_ticket(self, ticket):
        comments = []
        for when, author, field, old_value, new_value, permanent in ticket.get_changelog():
            if field != 'comment':
                continue
            comments.append((when, author, new_value))
        return comments
    
    def assert_number_of_comments_for_ticket(self, nr_comments, ticket):
        self.assert_equals(nr_comments, len(self.comments_for_ticket(ticket)))
    
    def fake_captcha_error(self):
        return 'Please fill in the CAPTCHA so we know you are not a spammer.'
    
    # --- new ticket creation --------------------------------------------------
    
    def test_can_insert_captcha_when_creating_a_new_ticket(self):
        response = self.simulate_request(self.request('/newticket', method='GET'))
        self.assert_equals([], response.trac_warnings())
        self.assert_fake_captcha_is_visible(response)
    
    def test_can_create_a_ticket_if_captcha_was_entered_correctly(self):
        req = self.post_request('/newticket', field_summary='Foo', 
                                fake_captcha='open sesame')
        response = self.simulate_request(req)
        self.assert_equals(303, response.code())
        self.assert_number_of_tickets(1)
    
    def test_reject_ticket_submission_if_captcha_not_entered_at_all(self):
        req = self.post_request('/newticket', field_summary='Foo')
        response = self.simulate_request(req)
        self.assert_equals([self.fake_captcha_error()], response.trac_warnings())
        self.assert_fake_captcha_is_visible(response)
        self.assert_number_of_tickets(0)
    
    # --- ticket comments ------------------------------------------------------
    
    def add_ticket(self):
        ticket = Ticket(self.env)
        ticket['summary'] = 'fnord'
        ticket.insert()
        return ticket
    
    def test_can_insert_captcha_before_adding_a_comment(self):
        ticket = self.add_ticket()
        self.grant_permission('anonymous', 'TICKET_APPEND')
        response = self.simulate_request(self.request('/ticket/%d' % ticket.id))
        self.assert_equals([], response.trac_warnings())
        self.assert_fake_captcha_is_visible(response)
    
    def generation_string(self, ticket):
        return str(ticket.time_changed.replace(microsecond=0))
    
    def post_comment(self, ticket, comment, **kwargs):
        req = self.post_request('/ticket/%d' % ticket.id, comment=comment, 
                                action='leave', ts=self.generation_string(ticket), 
                                **kwargs)
        return self.simulate_request(req)
    
    def test_reject_comment_if_captcha_not_entered_at_all(self):
        ticket = self.add_ticket()
        self.grant_permission('anonymous', 'TICKET_APPEND')
        response = self.post_comment(ticket, 'foo'  )
        self.assert_equals(200, response.code())
        self.assert_equals([self.fake_captcha_error()], response.trac_warnings())
        self.assert_fake_captcha_is_visible(response)
        self.assert_number_of_comments_for_ticket(0, Ticket(self.env, tkt_id=ticket.id))
    
    def test_can_add_a_comment_if_captcha_was_entered_correctly(self):
        ticket = self.add_ticket()
        self.grant_permission('anonymous', 'TICKET_APPEND')
        response = self.post_comment(ticket, 'foo', fake_captcha='open sesame')
        self.assert_equals(303, response.code())
        self.assert_number_of_comments_for_ticket(1, Ticket(self.env, tkt_id=ticket.id))
    
    # --- ticket modification --------------------------------------------------
    
    def post_ticket_modification(self, ticket, **kwargs):
        fields = {}
        for key, value in kwargs.items():
            argument_name = key == 'fake_captcha' and key or 'field_' + key
            fields[argument_name] = value
        for key in ('summary', 'type', 'priority', 'component', 'milestone'):
            fields.setdefault('field_' + key, ticket[key])
        req = self.post_request('/ticket/%d' % ticket.id, 
                                action='leave', ts=self.generation_string(ticket), 
                                **fields)
        return self.simulate_request(req)
    
    def test_can_reject_ticket_modification_if_captcha_not_entered_at_all(self):
        ticket = self.add_ticket()
        self.grant_permission('anonymous', 'TICKET_CHGPROP')
        response = self.post_ticket_modification(ticket, keywords='foobar')
        self.assert_equals(200, response.code())
        self.assert_equals([self.fake_captcha_error()], response.trac_warnings())
        self.assert_fake_captcha_is_visible(response)
        self.assert_equals('', Ticket(self.env, ticket.id)['keywords'] or '')
    
    def test_can_modify_ticket_if_captcha_was_entered_correctly(self):
        ticket = self.add_ticket()
        self.grant_permission('anonymous', 'TICKET_CHGPROP')
        response = self.post_ticket_modification(ticket, keywords='foobar', 
                                                 fake_captcha='open sesame')
        self.assert_equals(303, response.code())
        self.assert_equals('foobar', Ticket(self.env, ticket.id)['keywords'])
    
    # --- can skip captcha with sufficient privileges  -------------------------
    
    def test_no_captcha_on_new_ticket_page_if_user_has_captcha_skip_permission(self):
        self.grant_permission('anonymous', 'CAPTCHA_SKIP')
        response = self.simulate_request(self.request('/newticket', method='GET'))
        self.assert_equals([], response.trac_warnings())
        self.assert_false(self.is_fake_captcha_visible(response))
    
    def test_can_create_a_ticket_without_captcha_if_user_has_captcha_skip(self):
        self.grant_permission('anonymous', 'CAPTCHA_SKIP')
        req = self.post_request('/newticket', field_summary='Foo')
        response = self.simulate_request(req)
        self.assert_equals(303, response.code())
        self.assert_number_of_tickets(1)
    
    # --- can show errors ------------------------------------------------------
    
    def test_can_display_errors_if_captcha_was_entered_incorrectly(self):
        req = self.post_request('/newticket', field_summary='Foo', 
                                fake_captcha='bad captcha')
        response = self.simulate_request(req)
        self.assert_equals([self.fake_captcha_error()], response.trac_warnings())
        self.assert_fake_captcha_is_visible(response)
        self.assert_contains('bad captcha', response.html())
        self.assert_number_of_tickets(0)

