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

__all__ = ['domain_functions', 'json']

try:
    import json as json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        json = None


# add_domain was introduced in Trac 0.12
try:
    from trac.util.translation import domain_functions
except ImportError:
    from trac.util.translation import gettext_noop
    
    def domain_functions(domain, *symbols):
        _functions = {
          '_': gettext_noop,
          'add_domain': lambda env_path, locale_dir: None,
          }
        return [_functions[s] for s in symbols]

