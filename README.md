This is an archived repository: I do not use this code anymore and I won't spend time on development/maintenance. Maybe code from this repo will be useful to someone - feel free to copy what you need (MIT license).

---

# Trac Captcha

TracCaptcha is a Trac plugin to embed a [captcha](http://en.wikipedia.org/wiki/CAPTCHA) in the ticket page in addition to Trac's regular permission checks so that spammers are kept out.

**"It just works":** Installation and configuration is very simple, just install the egg and put two configuration options in your trac.ini. No database changes required.

**Batteries included:** The popular [reCAPTCHA](http://www.google.com/recaptcha) system is supported out of the box.
Technically it's a plugin - if you don't like it you're free to use any other plugin while still leverage the benefits from the general captcha infrastructure.

**Does not annoy users:** After the user entered the captcha once, he does not have
to solve the captcha again for the same ticket when he just clicks 'preview'.
Also you can configure exempt certain users or groups (e.g. 'all authenticated 
users') from the captchas just by using Trac's permission system.

**Easy to extend:** Protecting an additional page with a captcha is very simple. Implementing captchas for the ticket module took only [20 lines of code](https://github.com/FelixSchwarz/trac-captcha/blob/0a0823bee8a128554cd2857bc44e8dc705d39d1f/trac_captcha/ticket.py#L35-L53)! Captchas for the DiscussionPlugin needed [21 lines of code](https://github.com/FelixSchwarz/trac-captcha/blob/1744acb8d087702e7f46f0e8188cf3e69e4ca778/contrib/tracdiscussion/tracdiscussion_captcha/plugin.py#L34-L60)! Currently supported plugins:

* AccountManager (registration)
* DiscussionPlugin" TracDiscussion

Read "Contributed Plugins" for more information about plugin support.

'''Easy to write custom captchas:''' If you don't like reCAPTCHA, you can still use the generic infrastructure with all its features: You implement the code to generate the captcha and validate the user's input. TracCaptcha will take care of displaying your plugin in all supported pages!
The whole code is licensed under the very liberal [MIT license](http://en.wikipedia.org/wiki/MIT_License) so you can use the API in your own code without problems.

### Download and Configuration
 * tar.gz: http://pypi.python.org/pypi/TracCaptcha

Enable the macro in your trac.ini:
```
[components]
trac_captcha.* = enabled
# only necessary if you want to use reCAPTCHA
trac_recaptcha.* = enabled

[recaptcha]
# add here the keys you got from http://www.google.com/recaptcha/admin
public_key = ...
private_key = ...
# optional: reCAPTCHA widget theme (red, white, blackglass, clean)
# theme = red
# optional: omit non-Javascript fallback (stops some spammers), default: False
# require_javascript = True
```

If you want to exempt some users from the captcha, grant them the CAPTCHA_SKIP privilege. TICKET_ADMINs (Trac 0.13+) and TRAC_ADMINs automatically have this privilege so they will never see a captcha. Also a user only needs to solve the captcha once per modification (so you can click 'preview' as often as you like without having to solve the captcha all over again).

### Dependencies and Compatibility
 * Python 2.3-2.6
 * [Trac](https://trac.edgewall.org) 0.11 or 0.12
 * ''optional, just to run the tests'': TracDevPlatform Plugin
 * ''optional, for Python < 2.5'': [PyCrypto](http://www.pycrypto.org) for better security on Python 2.3 and 2.4
 * ''optional, for Python < 2.6'': reCAPTCHA theme selection via trac.ini requires [simplejson](http://code.google.com/p/simplejson/) (Python [2.3](http://pypi.python.org/pypi/simplejson/2.0.5), [2.4](http://pypi.python.org/pypi/simplejson/2.1.0) or [2.5](http://pypi.python.org/pypi/simplejson/))



### Supporting other Plugins
TracCaptcha is focussed on supporting the core Trac as released on [http://trac.edgewall.org](http://trac.edgewall.org). However I think also other Trac plugins can benefit from having a captcha. To learn more about other plugins and their configuration, please read [wiki:"contributed plugins"].

If you want to integrate a yet unsupported Trac plugin, you need a component similar to this one:
```python

class MyPluginCaptcha(Component):
    
    implements(ITemplateStreamFilter)

    # --- ITemplateStreamFilter ------------------------------------------------
    
    def filter_stream(self, req, method, filename, stream, data):
        if filename != 'plugin_template_filename.html':
            return stream
        transformer = Transformer('//div[@class="buttons"]')
        return TracCaptchaController(self.env).inject_captcha_into_stream(req, stream, transformer)

    # --- captcha validation --------------------------------------------------
    
    # you need to implement an interface of 'MyPlugin' so the method name 'validation_example' is
    # just an example. Also the parameters and the return codes depend on the plugin-specific 
    # interface
    # On example for a suitable interface is {{{trac.ticket.api.ITicketManipulator}}}'s 
    # validate_ticket method.
    def validation_example(self, req):
        error_message = TracCaptchaController(self.env).check_captcha_solution(req)
        if error_message is None:
            # captcha was validated successfully
            return True
        # user did not solve the captcha
        return False

```


### Contributed Plugins

**You need at least TracCaptcha 0.2 to use contributed plugins!**

I want to help other trac plugins to integrate TracCaptcha. However the 'glue code' for these plugins is not contained in the main TracCaptcha plugin because:

- Avoiding additional dependencies (also for the test runs) is much easier if these are separate plugins.
- The quality of these plugins really depends on the number of interested users. Bad plugins should not cause a bad reputation for the main plugin. If you use other plugins, please consider writing the necessary glue code and create a ticket so your code is available to others as well.
- Other plugins might have different licenses, so encapsulating the specific code in separate plugins prevents 'license pollution' of the main plugin.

These 'glue code' plugins can be found in the [contrib directory](https://github.com/FelixSchwarz/trac-captcha/tree/master/contrib). Please note that I don't use many external plugins on a regular basis so the quality of the integration code might not be as good as the main TracCaptcha plugin. Also the additional tests for these plugins are not run in the build server yet (see #25).

#### AccountManager
The [Account Manager Plugin](http://trac-hacks.org/wiki/AccountManagerPlugin) implements a user management infrastructure in Trac. On top of that, it implements some features like 'password change for users', 'web-based user creation', 'form-based login' and 'web-based user registration'. Currently the '''captcha [plugin](https://github.com/FelixSchwarz/trac-captcha/tree/master/contrib/accountmanager) only cares about new user registration! '''

To enable the captcha, please add these lines to your trac.ini:
``` 
[components]
accountmanager_captcha.* = enabled
``` 

#### DiscussionPlugin
The [DiscussionPlugin](http://trac-hacks.org/wiki/DiscussionPlugin) provides a simple forum implementation. The captcha is displayed when creating a new topic or posting a reply. To enable the captcha, please add these lines to your trac.ini:
``` 
[components]
tracdiscussion_captcha.* = enabled
``` 

Due to issues in the {{{IDiscussionFilter}}} interface, the captcha is only validated when you do the final submit, not for previewed topics/replies. This also means the captcha is shown every time when clicking preview, even when the users solved it before. 



### Captcha does not block all spammers?

Even with enabled TracCaptcha you might still see some spam in your Trac instance. I got regularly some spam tickets here for example (before 0.3.1). This are my observations:
 * Spammers usually try automated spamming first (this fails because of the captcha) but fall back to some kind of manual mode where a human solves the captcha.
 * reCAPTCHA doesn't seem to be broken. There are virtually no wrong captcha solutions as you would expect if the captcha had been cracked by some algorithm.
Of course no captcha can (should) stop humans. However a good captcha will increase the cost of spamming (because it remove the scaling-effect of algorithms) which hopefully leads to less spamming.

In TracCaptcha 0.3.1 you can require Javascript for reCAPTCHA (omit the noscript section). This feature stopped an annoying spammer in March 2011 who used a semi-automated solution. He actually solved the CAPTCHA anyway (manual work!) but his spam program failed to submit the data to the correct URL. To enforce Javascript for reCAPTCHA, add this option in your trac.ini:
```
[recaptcha]
…
require_javascript = True
```
I believe this does not affect visually impaired users as reCAPTCHA provides an audio challenge anyway.

I also noticed that some spammers try to find Trac instances but querying Google for pages with the '/newticket' URL so you can try to ensure that Google does not index your new ticket page (which does not contain useful information anyway). To do that add this to your {{{robots.txt}}} file:
```
# add the Trac URL prefix if necessary, for example
#   /opensource/projects/trac_captcha/newticket
# for the TracCaptcha instance.
Disallow: /newticket
```


### Writing your own CAPTCHA

If you don't like to use the reCAPTCHA service, you can write your own captcha very easily (if you consider building a good captcha easy). The TracCaptcha plugin still takes care about inserting your captcha in the appropriate pages, hiding it if it was already solved once and skipping it for users who have the CAPTCHA_SKIP privilege.

Your captcha plugin must implement the ICaptcha interface:
```python
# trac_captcha.api
class CaptchaFailedError(Exception):
    def __init__(self, msg, captcha_data=None):
        ...

class ICaptcha(Interface):
    """Extension point interface for components that implement a specific 
    captcha."""
    
    def genshi_stream(self):
        "Return a Genshi stream which contains the captcha implementation."
    
    def assert_captcha_completed(self, req):
        """Check the request if the captcha was completed successfully. If the
        captcha is incomplete, a CaptchaFailedError is raised."""
```

When you deploy your plugin, tell TracCaptcha to use your plugin implementation instead of reCAPTCHA which is the default:
```
[trac-captcha]
captcha = YourICaptchaClassName
```

