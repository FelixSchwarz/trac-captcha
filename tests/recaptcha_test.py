# -*- coding: UTF-8 -*-
# 
# The MIT License
# 
# Copyright (c) 2008-2010 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
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

import cgi
import re
try:
    from xml.etree import ElementTree
except ImportError:
    from elementtree import ElementTree

from babel import Locale
from genshi import HTML

from trac_captcha.api import CaptchaFailedError
from trac_captcha.compat import json
from trac_captcha.lib.attribute_dict import AttrDict
from trac_captcha.lib.testcase import PythonicTestCase
from trac_recaptcha.client import reCAPTCHAClient
from trac_recaptcha.genshi_widget import GenshiReCAPTCHAWidget
from trac_recaptcha.integration import reCAPTCHAImplementation, trac_hostname

from trac_captcha.test_util import CaptchaTest, EnvironmentStub, TracTest

# http://recaptcha.net/apidocs/captcha/client
example_http_snippet = '''
<script type="text/javascript"
   src="http://www.google.com/recaptcha/api/challenge?k=<your_public_key>">
</script>

<noscript>
   <iframe src="http://www.google.com/recaptcha/api/noscript?k=<your_public_key>"
       height="300" width="500" frameborder="0"></iframe><br>
   <textarea name="recaptcha_challenge_field" rows="3" cols="40">
   </textarea>
   <input type="hidden" name="recaptcha_response_field"
       value="manual_challenge">
</noscript>
'''

example_https_snippet = '''
<script type="text/javascript"
   src="https://www.google.com/recaptcha/api/challenge?k=<your_public_key>">
</script>

<noscript>
   <iframe src="https://www.google.com/recaptcha/api/noscript?k=<your_public_key>"
       height="300" width="500" frameborder="0"></iframe><br>
   <textarea name="recaptcha_challenge_field" rows="3" cols="40">
   </textarea>
   <input type="hidden" name="recaptcha_response_field"
       value="manual_challenge">
</noscript>
'''

# this is actually not literally copied from the reCAPTCHA site but assembled
# according to the instructions on http://recaptcha.net/apidocs/captcha/
example_http_snippet_with_error = '''
<script type="text/javascript"
   src="http://www.google.com/recaptcha/api/challenge?k=<your_public_key>&amp;error=incorrect-captcha-sol">
</script>

<noscript>
   <iframe src="http://www.google.com/recaptcha/api/noscript?k=<your_public_key>&amp;error=incorrect-captcha-sol"
       height="300" width="500" frameborder="0"></iframe><br>
   <textarea name="recaptcha_challenge_field" rows="3" cols="40">
   </textarea>
   <input type="hidden" name="recaptcha_response_field"
       value="manual_challenge">
</noscript>
'''


class FakeLog(object):
    debug_messages = []
    error_messages = []
    def __getattr__(self, method_name):
        attribute_name = method_name + '_messages'
        attribute = getattr(self.__class__, attribute_name)
        return lambda message: attribute.append(message)


class ReCAPTCHATestMixin(object):
    
    def assert_equivalent_xml(self, expected, actual):
        # We need to normalize all whitespace (XML pretty printing) as well as
        # dealing with <foo></foo> vs. <foo/>.
        # BeautifulSoup was not up to the task as it does not cope well with the
        # <foo/> variants (basically it assumes <foo>(other tags)</foo>)
        # ----------------------------------------------------------------------
        # initial idea from Fredrik Lundh
        # http://mail.python.org/pipermail/xml-sig/2003-November/009997.html
        def parse_as_normalized_xml(xml):
            xml_document = ElementTree.fromstring(xml)
            for node in xml_document.getiterator():
                if node.text:
                    node.text = node.text.strip()
                node.tail = None
            return xml_document
        first_xml = ElementTree.tostring(parse_as_normalized_xml(expected))
        second_xml = ElementTree.tostring(parse_as_normalized_xml(actual))
        # ----------------------------------------------------------------------
        self.assert_equals(first_xml, second_xml)
    
    def js_config_html(self, config=None):
        if config is None:
            return ''
        return '''<script type="text/javascript">
            RecaptchaOptions = %s;
        </script>''' % json.dumps(config)
    
    def recaptcha_snippet_as_xml(self, use_https=False, show_error=False, config=None):
        self.assert_false(use_https and show_error)
        if use_https:
            snippet_html = example_https_snippet
        elif show_error:
            snippet_html = example_http_snippet_with_error
        else:
            snippet_html = example_http_snippet
        config_html = self.js_config_html(config=config)
        return ('<span>' + config_html + snippet_html + '</span>').\
            replace('<br>', '<br/>').\
            replace('<your_public_key>', 'your_public_key').\
            replace('value="manual_challenge">', 'value="manual_challenge" />')


class GenshiReCAPTCHAWidgetTest(PythonicTestCase, ReCAPTCHATestMixin):
    
    def setUp(self):
        self.super()
        FakeLog.errors = []
    
    def widget(self, public_key='foobar', use_https=False, error=None, js_config=None):
        return GenshiReCAPTCHAWidget(public_key, use_https=use_https, error=error, 
                                     log=FakeLog(), js_config=js_config)
    
    def generated_xml(self, public_key='your_public_key', use_https=False, error=None, js_config=None):
        widget = self.widget(public_key, use_https=use_https, error=error, js_config=js_config)
        return unicode(widget.xml())
    
    def test_can_generate_recaptcha_html(self):
        expected_xml = self.recaptcha_snippet_as_xml()
        self.assert_equivalent_xml(expected_xml, self.generated_xml())
    
    def test_can_generate_recaptcha_html_for_https(self):
        expected_xml = self.recaptcha_snippet_as_xml(use_https=True)
        self.assert_equivalent_xml(expected_xml, self.generated_xml(use_https=True))
    
    def test_can_generate_recaptcha_html_with_error_parameter(self):
        expected_xml = self.recaptcha_snippet_as_xml(show_error=True)
        generated_xml = self.generated_xml(error='incorrect-captcha-sol')
        self.assert_equivalent_xml(expected_xml, generated_xml)
    
    # --- theme support --------------------------------------------------------
    
    def test_can_use_different_theme(self):
        recaptcha_js_config = dict(theme='blueberry')
        expected_xml = self.recaptcha_snippet_as_xml(config=recaptcha_js_config)
        generated_xml = self.generated_xml(js_config=recaptcha_js_config)
        self.assert_equivalent_xml(expected_xml, generated_xml)
    
    def do_without_json(self, callable):
        import trac_recaptcha.genshi_widget
        old_json_symbol = trac_recaptcha.genshi_widget.json
        trac_recaptcha.genshi_widget.json = None
        try:
            callable()
        finally:
            trac_recaptcha.genshi_widget.json = old_json_symbol
    
    def test_log_error_when_specifying_theme_without_simplejson_installed(self):
        def test():
            expected_xml = self.recaptcha_snippet_as_xml()
            generated_xml = self.generated_xml(js_config=dict(theme='blueberry'))
            self.assert_equivalent_xml(expected_xml, generated_xml)
            self.assert_equals(1, len(FakeLog.error_messages))
            self.assert_contains('simplejson', FakeLog.error_messages[0])
        self.do_without_json(test)
    
    def test_ignore_logging_if_no_log_configured(self):
        def test():
            expected_xml = self.recaptcha_snippet_as_xml()
            widget = GenshiReCAPTCHAWidget('your_public_key', js_config=dict(theme='blueberry'))
            generated_xml = unicode(widget.xml())
            self.assert_equivalent_xml(expected_xml, generated_xml)
        self.do_without_json(test)
    
    # --- widget languages -----------------------------------------------------
    
    def test_can_set_widget_language(self):
        recaptcha_js_config = dict(lang='fr')
        expected_xml = self.recaptcha_snippet_as_xml(config=recaptcha_js_config)
        generated_xml = self.generated_xml(js_config=recaptcha_js_config)
        self.assert_equivalent_xml(expected_xml, generated_xml)
    
    def test_do_not_log_error_about_language_when_simplejson_not_installed(self):
        def test():
            expected_xml = self.recaptcha_snippet_as_xml()
            generated_xml = self.generated_xml(js_config=dict(lang='fr'))
            self.assert_equivalent_xml(expected_xml, generated_xml)
            self.assert_equals(0, len(FakeLog.error_messages))
            self.assert_equals(1, len(FakeLog.debug_messages))
            self.assert_contains('simplejson is not available', FakeLog.debug_messages[0])
        self.do_without_json(test)


class reCAPTCHAClientTest(PythonicTestCase):
    
    def setUp(self):
        self.super()
        self.request_sent = False
    
    def client(self):
        return reCAPTCHAClient('foo')
    
    def fake_request(self, expected_remote_ip, expected_challenge, expected_response,
                     server_response='true\n\n'):
        def request_probe(url, parameters):
            self.assert_equals('http://www.google.com/recaptcha/api/verify', url)
            expected = dict(privatekey='foo', remoteip=expected_remote_ip,
                            challenge=expected_challenge, response=expected_response)
            self.assert_equals(expected, parameters)
            self.request_sent = True
            return server_response
        return request_probe
    
    def test_sends_correct_request_to_recaptcha_servers(self):
        probe = self.fake_request('127.0.0.42', 'a challenge', 'bar')
        self.client().verify('127.0.0.42', 'a challenge', 'bar', probe)
        self.assert_true(self.request_sent)
    
    def assert_invalid(self, response):
        parse = lambda: self.client().assert_server_accepted_solution(response)
        self.assert_raises(CaptchaFailedError, parse)
    
    def test_raises_exception_on_failed_verification(self):
        self.assert_invalid('false\nfoobar')
        self.assert_invalid('false')
    
    def test_raises_exception_for_failed_verification_without_reason(self):
        self.assert_invalid('')
    
    def test_ignores_additional_lines_of_server_response(self):
        self.assert_invalid('false\nfoobar\future information')
    
    def test_do_not_ask_server_if_no_parameters_given(self):
        for challenge, response in (('', ''), ('  ', ''), ('', ' '), (None, ''), ('', None)):
            probe = self.fake_request('should never be called', challenge, response)
            parse = lambda: self.client().verify('127.0.0.42', challenge, response, probe)
            self.assert_raises(CaptchaFailedError, parse)
            self.assert_false(self.request_sent)



class HostnameFinder(TracTest):
    def setUp(self):
        self.super()
        self.env = EnvironmentStub()
    
    def test_can_extract_hostname_from_wsgi_environment(self):
        req = self.request('/', request_attributes={'trac.base_url': 'http://foo.bar/trac'})
        self.assert_equals('foo.bar', trac_hostname(req))
    
    def test_can_extract_hostname_http_host_header(self):
        req = self.request('/')
        req._inheaders = [('host', 'foo.baz')]
        self.assert_equals('foo.baz', req.get_header('Host'))
        
        self.assert_equals('foo.baz', trac_hostname(req))
    
    def test_can_extract_hostname_wsgi_server_name(self):
        req = self.request('/', request_attributes={'SERVER_NAME': 'foo.bar'})
        self.assert_equals('foo.bar', trac_hostname(req))
    
    def test_uses_configured_base_url_preferrably(self):
        environ = {'trac.base_url': 'http://foo.base_url/trac',
                   'SERVER_NAME': 'foo.servername'}
        req = self.request('/', request_attributes=environ)
        self.assert_equals('foo.base_url', trac_hostname(req))
    
    def test_prefers_host_header_over_wsgi_server_name(self):
        req = self.request('/', request_attributes={'SERVER_NAME': 'foo.servername'})
        req._inheaders = [('host', 'foo.header')]
        self.assert_equals('foo.header', trac_hostname(req))



class reCAPTCHAImplementationTest(CaptchaTest, ReCAPTCHATestMixin):
    
    def setUp(self):
        self.super()
        self.enable_captcha(reCAPTCHAImplementation)
        self.env.config.set('recaptcha', 'public_key', '1234567')
        self.env.config.set('recaptcha', 'private_key', '1234567')
    
    def client_with_probe(self, real_probe):
        client = reCAPTCHAClient
        real_verify = client.verify
        def fake_verify(self, remote_ip, challenge, response, probe=None):
            real_verify(self, remote_ip, challenge, response, probe=real_probe)
        client.verify = fake_verify
        return client
    
    def client_with_injected_probe(self, expected_parameters):
        options = AttrDict(request_sent=False)
        def probe(url, parameters):
            self.assert_equals(expected_parameters, parameters)
            options.request_sent = True
            return 'true\n'
        client = self.client_with_probe(probe)
        client.options = options
        return client
    
    def test_can_extract_remote_ip_private_key_and_form_data(self):
        self.env.config.set('recaptcha', 'private_key', '1234567890')
        req = self.request('/', recaptcha_challenge_field='foo',
                           recaptcha_response_field='bar')
        req.environ['REMOTE_ADDR'] = '192.168.137.1'
        expected = dict(privatekey='1234567890', remoteip='192.168.137.1',
                        challenge='foo', response='bar')
        client = self.client_with_injected_probe(expected)
        reCAPTCHAImplementation(self.env).assert_captcha_completed(req, client)
        self.assert_true(client.options.request_sent)
    
    def test_displays_error_message_instead_of_captcha_if_no_public_key_was_set(self):
        self.env.config.set('recaptcha', 'public_key', '')
        generated_xml = self.generated_xml()
        self.assert_contains('No public key', generated_xml)
        self.assert_contains('sign up', generated_xml)
    
    def test_shows_signup_link_if_no_public_key_was_set(self):
        self.env.config.set('recaptcha', 'public_key', '')
        req = self.request('/', request_attributes={'trac.base_url': 'http://example.com/trac'})
        generated_xml = self.generated_xml(req)
        actual_link = re.search('href="(?P<url>.*?)"', generated_xml).group('url')
        actual_url, actual_parameters = actual_link.split('?', 1)
        
        self.assert_equals('http://www.google.com/recaptcha/admin', actual_url)
        expected_parameters = dict(app='TracCaptcha', domain='example.com')
        actual_parameters = dict(cgi.parse_qsl(actual_parameters))
        self.assert_equals(expected_parameters, actual_parameters)
    
    def assert_captcha_rejected(self, req, client):
        verify_captcha = lambda: reCAPTCHAImplementation(self.env).assert_captcha_completed(req, client)
        e = self.assert_raises(CaptchaFailedError, verify_captcha)
        self.assert_contains(u'reCAPTCHA private key is missing', e.msg)
        self.assert_equals('invalid-site-private-key', e.captcha_data['error_code'])
    
    def test_do_not_callback_to_recaptcha_if_no_private_key_set(self):
        self.env.config.set('recaptcha', 'private_key', '')
        
        req = self.request('/', recaptcha_challenge_field='foo',
                           recaptcha_response_field='bar')
        probe = lambda url, parameters: self.fail('Should not call back to recaptcha servers!')
        self.assert_captcha_rejected(req, self.client_with_probe(probe))
    
    # --- themes ---------------------------------------------------------------
    
    def generated_xml(self, req=None):
        req = req or self.request('/')
        stream = reCAPTCHAImplementation(self.env).genshi_stream(req)
        return unicode(HTML(stream))
    
    def test_can_select_different_theme_in_trac_ini(self):
        self.env.config.set('recaptcha', 'theme', 'blueberry')
        self.assert_contains('{"theme": "blueberry"}', self.generated_xml())
    
    # --- i18n -----------------------------------------------------------------
    
    def test_can_retrieve_locale_from_users_locale(self):
        req = self.request('/')
        req.locale = Locale('fr')
        self.assert_contains('{"lang": "fr"}', self.generated_xml(req))
    
    def test_ignore_locale_if_babel_not_installed(self):
        req = self.request('/')
        req.locale = None
        self.assert_false('RecaptchaOptions' in self.generated_xml(req))
    
    # --- HTTPS ----------------------------------------------------------------
    
    def test_uses_recaptcha_secure_servers_if_request_uses_https(self):
        self.env.config.set('recaptcha', 'public_key', 'your_public_key')
        expected_xml = self.recaptcha_snippet_as_xml(use_https=True)
        req = self.request('/', request_attributes={'wsgi.url_scheme': 'https'})
        self.assert_equivalent_xml(expected_xml, self.generated_xml(req))

