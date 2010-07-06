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

try:
    from xml.etree import ElementTree
except ImportError:
    from elementtree import ElementTree

from babel import Locale
from genshi import HTML
from trac_captcha.api import CaptchaFailedError
from trac_captcha.compat import json
from trac_captcha.lib.testcase import PythonicTestCase
from trac_recaptcha.recaptcha import GenshiReCAPTCHAWidget, reCAPTCHAClient, \
    reCAPTCHAImplementation
from trac_captcha.test_util import CaptchaTest

# http://recaptcha.net/apidocs/captcha/client.html
example_http_snippet = '''
<script type="text/javascript"
   src="http://api.recaptcha.net/challenge?k=<your_public_key>">
</script>

<noscript>
   <iframe src="http://api.recaptcha.net/noscript?k=<your_public_key>"
       height="300" width="500" frameborder="0"></iframe><br>
   <textarea name="recaptcha_challenge_field" rows="3" cols="40">
   </textarea>
   <input type="hidden" name="recaptcha_response_field" 
       value="manual_challenge">
</noscript>
'''

example_https_snippet = '''
<script type="text/javascript"
   src="https://api-secure.recaptcha.net/challenge?k=<your_public_key>">
</script>

<noscript>
   <iframe src="https://api-secure.recaptcha.net/noscript?k=<your_public_key>"
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
   src="http://api.recaptcha.net/challenge?k=<your_public_key>&amp;error=incorrect-captcha-sol">
</script>

<noscript>
   <iframe src="http://api.recaptcha.net/noscript?k=<your_public_key>&amp;error=incorrect-captcha-sol"
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
        import trac_recaptcha.recaptcha
        old_json_symbol = trac_recaptcha.recaptcha.json
        trac_recaptcha.recaptcha.json = None
        try:
            callable()
        finally:
            trac_recaptcha.recaptcha.json = old_json_symbol
    
    def test_log_error_when_specifying_theme_without_simplejson_installed(self):
        def test():
            expected_xml = self.recaptcha_snippet_as_xml()
            generated_xml = self.generated_xml(js_config=dict(theme='blueberry'))
            self.assert_equivalent_xml(expected_xml, generated_xml)
            self.assert_equals(1, len(FakeLog.error_messages))
            self.assert_contains('simplejson', FakeLog.error_messages[0])
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
            self.assert_equals('http://api-verify.recaptcha.net/verify', url)
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


class reCAPTCHAImplementationTest(CaptchaTest, ReCAPTCHATestMixin):
    
    def setUp(self):
        self.super()
        self.enable_captcha(reCAPTCHAImplementation)
    
    def client_with_injected_probe(self, expected_parameters):
        client = reCAPTCHAClient
        client.request_sent = False
        real_verify = client.verify
        def probe(url, parameters):
            self.assert_equals(expected_parameters, parameters)
            client.request_sent = True
            return 'true\n'
        def fake_verify(self, remote_ip, challenge, response):
            real_verify(self, remote_ip, challenge, response, probe=probe)
        client.verify = fake_verify
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
        self.assert_true(client.request_sent)
    
    # --- themes ---------------------------------------------------------------
    
    def test_can_select_different_theme_in_trac_ini(self):
        self.env.config.set('recaptcha', 'theme', 'blueberry')
        req = self.request('/')
        stream = reCAPTCHAImplementation(self.env).genshi_stream(req)
        self.assert_contains('{"theme": "blueberry"}', unicode(HTML(stream)))
    
    # --- i18n -----------------------------------------------------------------
    
    def test_can_retrieve_locale_from_users_locale(self):
        req = self.request('/')
        req.locale = Locale('fr')
        stream = reCAPTCHAImplementation(self.env).genshi_stream(req)
        self.assert_contains('{"lang": "fr"}', unicode(HTML(stream)))
    
    def test_ignore_locale_if_babel_not_installed(self):
        req = self.request('/')
        req.locale = None
        stream = reCAPTCHAImplementation(self.env).genshi_stream(req)
        self.assert_false('RecaptchaOptions' in unicode(HTML(stream)))
    
    # --- HTTPS ----------------------------------------------------------------
    
    def test_uses_recaptcha_secure_servers_if_request_uses_https(self):
        self.env.config.set('recaptcha', 'public_key', 'your_public_key')
        req = self.request('/', request_attributes={'wsgi.url_scheme': 'https'})
        stream = reCAPTCHAImplementation(self.env).genshi_stream(req)
        expected_xml = self.recaptcha_snippet_as_xml(use_https=True)
        self.assert_equivalent_xml(expected_xml, unicode(stream))

