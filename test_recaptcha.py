#!/usr/bin/env python

import base64

public_key = '01Xc9K3BQ-n4iTFhXjLJsj7w=='
private_key = '38374547cd0661498f93a6801b5cbb5e'

def pad_string (str, block_size):
   numpad = block_size - (len (str) % block_size)
   return str + numpad * chr (numpad)

cleartext = 'foo@bar.com'
aes_key = base64.b16decode(private_key, casefold=True)
aes_iv = '\0' * 16

from Crypto.Cipher import AES
crypted = AES.new(aes_key, AES.MODE_CBC, aes_iv).encrypt(pad_string (cleartext, 16))
print repr(base64.encodestring(crypted))

print repr(AES.new(aes_key, AES.MODE_CBC, aes_iv).decrypt(crypted))

#AES encrypt the string. The private key is your AES encryption key. AES CBC mode is used with an initialization vector of 16 null bytes (in theory, using a common IV would allow an attacker to know if emails encrypted with the same key have a common 16 byte prefix. However, in order to decode both emails, the attacker still must solve a CAPTCHA. On the other hand an IV would make URLs significantly longer).

#    return AES.new (aes_key, AES.MODE_CBC, aes_iv).encrypt (_pad_string (str, 16))

