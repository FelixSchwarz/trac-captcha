# -*- coding: UTF-8 -*-
# 
# The MIT License
# 
# Copyright (c) 2010-2011 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
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

from cStringIO import StringIO
import re

from BeautifulSoup import BeautifulSoup
from trac.core import Component, ComponentMeta
from trac.perm import DefaultPermissionPolicy, PermissionCache, PermissionSystem
from trac.web.api import Request, RequestDone
from trac.web.main import RequestDispatcher

from trac_captcha.lib.testcase import PythonicTestCase


__all__ = ['mock_request', 'TracTest']

class MockResponse(object):
    
    def __init__(self):
        self.status_line = None
        self.headers = []
        self.body = StringIO()
    
    def code(self):
        string_code = self.status_line.split(' ', 1)[0]
        return int(string_code)
    
    def start_response(self, status, response_headers):
        self.status_line = status
        self.headers = response_headers
        return lambda data: self.body.write(data)
    
    def html(self):
        self.body.seek(0)
        body_content = self.body.read()
        self.body.seek(0)
        return body_content
    
    def trac_messages(self, message_type):
        soup = BeautifulSoup(self.html())
        message_container = soup.find(name='div', attrs=dict(id='warning'))
        if message_container is None:
            return []
        messages_with_tags = message_container.findAll('li')
        if len(messages_with_tags) > 0:
            strip_tags = lambda html: re.sub('^<li>(.*)</li>$', r'\1', unicode(html))
            return map(strip_tags, messages_with_tags)
        pattern = '<strong>%s:</strong>\s*(.*?)\s*</div>' % message_type
        match = re.search(pattern, unicode(message_container), re.DOTALL | re.IGNORECASE)
        if match is None:
            return []
        return [match.group(1)]
    
    def trac_warnings(self):
        return self.trac_messages('Warning')


def mock_request(path, request_attributes=None, **kwargs):
    request_attributes = request_attributes or {}
    wsgi_environment = {
        'SERVER_PORT': 4711,
        'SERVER_NAME': 'foo.bar',
        
        'REMOTE_ADDR': '127.0.0.1',
        'REQUEST_METHOD': request_attributes.pop('method', 'GET'),
        'PATH_INFO': path,
        
        'wsgi.url_scheme': 'http',
        'wsgi.input': StringIO(),
    }
    wsgi_environment.update(request_attributes)
    
    response = MockResponse()
    request = Request(wsgi_environment, response.start_response)
    request.captured_response = response
    request.args = kwargs
    return request


class TracTest(PythonicTestCase):
    
    def enable_ticket_subsystem(self):
        # ensure that all of trac's ticket components will be found by importing
        # them all.
        
        # TODO: Can we use setuptools for this? Query all of trac's entry points?
        import trac.ticket.api
        import trac.ticket.admin
        import trac.ticket.default_workflow
        import trac.ticket.model
        import trac.ticket.notification
        import trac.ticket.query
        import trac.ticket.report
        import trac.ticket.roadmap
        import trac.ticket.web_ui
    
    def disable_component(self, component):
        component_name = self.trac_component_name_for_class(component)
        self.env.config.set('components', component_name, 'disabled')
        self.clear_trac_rule_cache()
        if isinstance(component, (Component, ComponentMeta)):
            self.assert_false(self.env.is_component_enabled(component),
                             '%s is not disabled' % component_name)
    
    def enable_component(self, component):
        component_name = self.trac_component_name_for_class(component)
        self.env.config.set('components', component_name, 'enabled')
        self.clear_trac_rule_cache()
        if isinstance(component, (Component, ComponentMeta)):
            self.assert_true(self.env.is_component_enabled(component), 
                             '%s is not enabled' % component_name)
    
    def grant_permission(self, username, action):
        # DefaultPermissionPolicy will cache permissions for 5 seconds so we 
        # need to reset the cache
        DefaultPermissionPolicy(self.env).permission_cache = {}
        PermissionSystem(self.env).grant_permission(username, action)
        self.assert_true(self.has_permission(username, action))
    
    def has_permission(self, username, action):
        DefaultPermissionPolicy(self.env).permission_cache = {}
        return PermissionSystem(self.env).check_permission(action, username)
    
    def assert_has_permission(self, username, action):
        self.assert_true(self.has_permission(username, action))
    
    def assert_has_no_permission(self, username, action):
        self.assert_false(self.has_permission(username, action))
    
    def request(self, path, request_attributes=None, **kwargs):
        request = mock_request(path, request_attributes, **kwargs)
        request.perm = PermissionCache(self.env, username=request.remote_user)
        return request
    
    def post_request(self, *args, **kwargs):
        kwargs.setdefault('request_attributes', dict())
        kwargs['request_attributes']['method'] = 'POST'
        return self.request(*args, **kwargs)
    
    def simulate_request(self, req):
        process_request = lambda: RequestDispatcher(self.env).dispatch(req)
        self.assert_raises(RequestDone, process_request)
        response = req.captured_response
        response.body.seek(0)
        return response
    
    # --- private --------------------------------------------------------------
    
    def trac_component_name_for_class(self, component_or_name):
        if isinstance(component_or_name, basestring):
            return component_or_name
        class_name = str(component_or_name.__name__)
        return str(component_or_name.__module__ + "." + class_name).lower()
    
    def clear_trac_rule_cache(self):
        # self.env_rules is only generated once, further changes to the config
        # do not update the rules, so we need to reset it manually
        if hasattr(self.env, '_rules'):
            del self.env._rules


