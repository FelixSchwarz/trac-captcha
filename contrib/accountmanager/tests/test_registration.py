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

import os
import shutil
import tempfile

from acct_mgr.api import AccountManager
from trac_captcha.test_util import CaptchaTest, FakeCaptcha

from accountmanager_captcha.registration import AccountManagerRegistrationCaptcha

class AccountManagerRegistrationTest(CaptchaTest):
    
    def setUp(self):
        self.super()
        self.tempdir = tempfile.mkdtemp()
        self.enable_account_manager()
        self.enable_captcha(FakeCaptcha)
        self.enable_component(AccountManagerRegistrationCaptcha)
    
    def tearDown(self):
        shutil.rmtree(self.tempdir)
        self.super()
    
    def enable_account_manager(self):
        password_filename = os.path.join(self.tempdir, 'htpasswd')
        self.env.config.set('account-manager', 'password_file', password_filename)
        self.env.config.set('account-manager', 'password_store', 'HtPasswdStore')
        file(password_filename, 'wb').write('')
        self.enable_account_manager_modules()
    
    def enable_account_manager_modules(self):
        import acct_mgr.api
        import acct_mgr.htfile
        import acct_mgr.web_ui
        self.enable_component(acct_mgr.api.AccountManager)
        self.enable_component(acct_mgr.htfile.HtPasswdStore)
        self.enable_component(acct_mgr.web_ui.RegistrationModule)
    
    def parameters_for_account_registration(self, **kwargs):
        parameters =  dict(user='foo', password='bar', password_confirm='bar',
                           action='create')
        parameters.update(kwargs)
        return parameters
    
    def user_exists(self, username):
        return AccountManager(self.env).has_user(username)
    
    def assert_user_exists(self, username):
        self.assert_true(self.user_exists(username))
    
    def assert_user_does_not_exist(self, username):
        self.assert_false(self.user_exists(username))
    
    # --- registration page ----------------------------------------------------
    
    def test_can_insert_captcha_in_registration(self):
        response = self.simulate_request(self.request('/register'))
        self.assert_equals([], response.trac_warnings())
        self.assert_fake_captcha_is_visible(response)
    
    def test_reject_registration_if_captcha_was_not_solved_correctly(self):
        parameters = self.parameters_for_account_registration()
        req = self.post_request('/register', **parameters)
        response = self.simulate_request(req)
        self.assert_fake_captcha_warning_visible(response)
        self.assert_fake_captcha_is_visible(response)
        self.assert_user_does_not_exist('foo')
    
    def test_can_register_account_if_captcha_was_solved(self):
        parameters = self.parameters_for_account_registration(fake_captcha='open sesame')
        req = self.post_request('/register', **parameters)
        response = self.simulate_request(req)
        self.assert_equals(303, response.code())
        self.assert_user_exists('foo')
    
    # --- user administration page ---------------------------------------------
    
    def enable_account_manager_admin_page(self):
        # need also to load trac's admin component, otherwise the whole admin
        # panel dispatcher mechanism is not working...
        import trac.admin.web_ui
        import acct_mgr.admin
        self.enable_component(acct_mgr.admin.AccountManagerAdminPage)
    
    def test_admin_can_create_users_without_captcha(self):
        self.enable_account_manager_admin_page()
        self.grant_permission('foo', 'TRAC_ADMIN')
        parameters = self.parameters_for_account_registration(add='true')
        req = self.post_request('/admin/accounts/users', request_attributes=dict(REMOTE_USER='foo'), 
                                **parameters)
        req.perm.assert_permission('TRAC_ADMIN')
        response = self.simulate_request(req)
        self.assert_equals(200, response.code())
        self.assert_user_exists('foo')


