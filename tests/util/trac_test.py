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

from cStringIO import StringIO

from trac.perm import PermissionSystem, DefaultPermissionPolicy
from trac.web.api import Request, RequestDone
from trac.web.main import RequestDispatcher

from trac_captcha.lib.attribute_dict import AttrDict
from trac_captcha.lib.testcase import PythonicTestCase



class TracTest(PythonicTestCase):
    def setUp(self):
        self.super()
    
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
    
    def grant_permission(self, username, action):
        # DefaultPermissionPolicy will cache permissions for 5 seconds so we 
        # need to reset the cache
        DefaultPermissionPolicy(self.env).permission_cache = {}
        permission_system = PermissionSystem(self.env)
        permission_system.grant_permission(username, action)
        self.assert_true(permission_system.check_permission(action, username))
    
    def request(self, path):
        wsgi_environment = {
            'SERVER_PORT': 4711,
            'SERVER_NAME': 'foo.bar',
            
            # TODO: parameter
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': path,
            
            # TODO: what is wsgi.url_scheme?
            'wsgi.url_scheme': 'http',
            'wsgi.input': StringIO(),
        }
        
        response = AttrDict(code=None, headers=[], body=StringIO())
        def start_response(status, response_headers):
            response.code = status
            response.headers = response_headers
            return lambda data: response.body.write(data)
        
        request = Request(wsgi_environment, start_response)
        request.captured_response = response
        return request
    
    def simulate_request(self, req):
        process_request = lambda: RequestDispatcher(self.env).dispatch(req)
        self.assert_raises(RequestDone, process_request)
        response = req.captured_response
        response.body.seek(0)
        return response

