# -*- coding: utf-8 -*-
import math
import random
import base64
from Crypto.Cipher import AES
from pyDes import des, CBC, PAD_PKCS5


# DES加密
def DESEncrypt(s, key='XCE927=='):
    iv = b"\x01\x02\x03\x04\x05\x06\x07\x08"
    k = des(key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    encrypt_str = k.encrypt(s)
    return base64.b64encode(encrypt_str).decode()


# DES解密
def DESDecrypt(s, key='XCE927=='):
    s = base64.b64decode(s)
    iv = b"\x01\x02\x03\x04\x05\x06\x07\x08"
    k = des(key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    return k.decrypt(s)


# 获取随机字符串
def getRandomString(length):
    chs = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
    result = ''
    for i in range(0, length):
        result += chs[(math.floor(random.random() * len(chs)))]
    return result


# AES加密
def EncryptAES(s, key, iv='1' * 16, charset='utf-8'):
    key = key.encode(charset)
    iv = iv.encode(charset)
    BLOCK_SIZE = 16
    pad = lambda s: (s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE))
    raw = pad(s)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(bytes(raw, encoding=charset))
    return str(base64.b64encode(encrypted), charset)


# AES解密
def DecryptAES(s, key, iv='1' * 16, charset='utf-8'):
    key = key.encode(charset)
    iv = iv.encode(charset)
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypt = unpad(cipher.decrypt(base64.b64decode(s)))
    return str(decrypt, charset)


# 金智的AES加密过程
def AESEncrypt(data, key):
    return EncryptAES(getRandomString(64) + data, key, key)


# 金智的AES解密过程
def AESDecrypt(data, key):
    return DecryptAES(data, key)[64:]

