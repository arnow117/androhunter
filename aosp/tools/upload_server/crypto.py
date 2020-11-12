#!/usr/local/bin/python

import random
from Crypto.Cipher import AES
from binascii import hexlify,unhexlify
import struct
__author__ = 'devilk_r'

key_map = ['\x2b', '\x7e', '\x15', '\x16',
           '\x28', '\xae', '\xd2', '\xa6',
           '\xab', '\xf7', '\x15', '\x88',
           '\x09', '\xcf', '\x4f', '\x3c',
           '\x76', '\x49', '\xab', '\xac',
           '\x81', '\x19', '\xb2', '\x46',
           '\xce', '\xe9', '\x8e', '\x9b',
           '\x12', '\xe9', '\x19', '\x7d']

iv = ['\x00', '\x01', '\x02', '\x03',
      '\x04', '\x05', '\x06', '\x07',
      '\x08', '\x09', '\x0a', '\x0b',
      '\x0c', '\x0d', '\x0e', '\x0f']


def __encrypt(text, key):
    # length 16 key
    mode = AES.MODE_CBC
    encryptor = AES.new(key, mode, str(bytearray(iv)))
    ciphertext = encryptor.encrypt(text)
    return ciphertext


def __decrypt(text,key):
    mode = AES.MODE_CBC
    decryptor = AES.new(key, mode, str(bytearray(iv)))
    text = decryptor.decrypt(text)
    return text.rstrip('\0')


def get_key(string):
    s = map(ord, string)
    result = []
    for i in s:
        result.append(key_map[i])
    return str(bytearray(result))


def get_index():
    result = []
    for i in range(16):
        result.append(random.randint(0, 31))
    result = bytearray(result)
    return result


def encrypt(message,key):
    return hexlify(__encrypt(message+'\x00'*(16-len(message)%16), key))


def decrypt(message,key):
    return __decrypt(message, key)

if __name__ == '__main__':
    # print 'iv is '+print_bytearray(iv)
    s = encrypt('test', get_key('\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'))
    print unhexlify(s)
    # a2b_hex(text)
    print decrypt(s, get_key('\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'))
    # 94bb51878f8db28acb5ef0754f193c7c
