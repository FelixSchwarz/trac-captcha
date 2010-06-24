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

from datetime import datetime, timedelta
from hmac import HMAC
import re

from trac.util import hex_entropy
from trac.util.datefmt import localtz, to_timestamp, utc

__all__ = ['CryptoBox']


class CryptoBox(object):
    
    def __init__(self, key=None):
        self.key = key
        self.hash_algorithm = None
    
    def generate_key(self):
        return hex_entropy(32)
    
    def generate_token(self):
        message = self.token_payload()
        return message + '||' + self.sign_message(message)
    
    def is_token_valid(self, token):
        if not self.is_syntactically_valid_token(token):
            return False
        message, hash = self.parse_token(token)
        if not self.is_correct_hash(hash, message):
            return False
        return self.token_is_valid_until(message) >= datetime.now(localtz)
    
    # --- private API ----------------------------------------------------------
    
    def best_hash_algorithm(self):
        if self.hash_algorithm is not None:
            return self.hash_algorithm
        try:
            from hashlib import sha512
            self.hash_algorithm = sha512
            return sha512
        except ImportError:
            pass
        # no new hashlib, try pycrypto's sha256
        try:
            from Crypto.Hash import SHA256
            self.hash_algorithm = SHA256
            return SHA256
        except ImportError:
            pass
        # fall back to sha1
        import sha
        self.hash_algorithm = sha
        return sha
    
    def sign_message(self, message):
        if self.key is None:
            self.key = self.generate_key()
        return HMAC(self.key, message, digestmod=self.best_hash_algorithm()).hexdigest()
    
    def token_payload(self, valid_until=None):
        if valid_until is None:
            valid_until = datetime.now(localtz) + timedelta(hours=4)
        return str(to_timestamp(valid_until))
    
    def is_syntactically_valid_token(self, token):
        if not hasattr(token, 'split'):
            return False
        parts = token.split('||')
        if len(parts) != 2:
            return False
        return True
    
    def token_is_valid_until(self, timestamp):
        if re.search('\D', timestamp) is not None:
            return datetime.fromtimestamp(0, utc)
        return datetime.fromtimestamp(int(timestamp), utc)
    
    def parse_token(self, token):
        return token.split('||', 1)
    
    def is_correct_hash(self, hash, message):
        return hash == self.sign_message(message)


