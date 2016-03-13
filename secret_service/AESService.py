from Crypto.Cipher import AES
from Crypto.Hash import SHA512
from Crypto.Random import OSRNG
from math import ceil
from time import sleep
import random

def _genkey(key, length):
    if len(key) >= length:
        return key[:length]
    return _mac(key,length)

def _mac(key, length):
    h = SHA512.new(key)
    ret = h.digest()
    return ret[:length]


def _get_message_from_lenmes(m, divisor):
    i = m.find(divisor)
    if i < 0:
        raise ValueError("seperator not found")
    l = _nonNillStringToNum(m[:i])
    return m[i+1:l+i+1]

def _numToNonNillString(x):
    ret = ""
    base = 255
    while x!=0:
        ret = chr((x%base) + 1) + ret
        x /= base
    return ret

def _nonNillStringToNum(s):
    ret = 0
    base = 255
    for c in s:
        ret *= base
        ret += ord(c)-1
    return ret

#format is: 16 bytes of hash, 16 bytes of iv, encrypted[message length, whitespace, message, padding]

def encrypt(key, mes, extrapaddingmax = 0):
    k = _genkey(key, 16)
    iv = OSRNG.new().read(AES.block_size)
    aes = AES.new(k, AES.MODE_CBC, iv)
    #message
    m = mes
    #length
    m = _numToNonNillString(len(m)) + chr(0) + m
    #pad
    extrapadding = random.randint(extrapaddingmax/2,extrapaddingmax)
    m += "".join(map(lambda a:chr(random.randint(0,255)),xrange((16 * (extrapadding + int(ceil(len(m)/16.0)))-len(m)))))
    #encrypt
    m = aes.encrypt(m)
    #iv
    m = iv + m
    #mac
    m = _mac(m, 16) + m
    return m


def decrypt(key, cipher):
    sleep(0.1)
    k = _genkey(key, 16)
    if len(cipher)%16 != 0:
        raise StandardError("Bad Cipher!, len {}".format(len(cipher)))
    mac, m = cipher[:16],cipher[16:]

    #validation
    try:
        validation = _mac(m, 16)
    except ValueError:
        validation = None
    if validation is None or validation != mac:
        raise StandardError("Validation Error!")

    #get iv
    iv, m = m[:16], m[16:]

    #decrypt
    aes = AES.new(k, AES.MODE_CBC, iv)
    m = aes.decrypt(m)
    mes = _get_message_from_lenmes(m, chr(0))
    return mes