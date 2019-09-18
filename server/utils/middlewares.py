import zlib
from functools import wraps

from Crypto.Cipher import AES

from .util import get_chunk


def compression_middleware(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        b_request = zlib.decompress(request)
        b_response = func(b_request, *args, **kwargs)
        return zlib.compress(b_response)
    return wrapper


def encryption_middleware(func):
    @wraps(func)
    def wrapper(encrypted_request, *args, **kwargs):
        nonce, encrypted_request = get_chunk(encrypted_request, 16)
        key, encrypted_request = get_chunk(encrypted_request, 16)
        tag, encrypted_request = get_chunk(encrypted_request, 16)

        cipher = AES.new(key, AES.MODE_EAX, nonce)

        raw_request = cipher.decrypt_and_verify(encrypted_request, tag)
        response = func(raw_request, *args, **kwargs)

        cipher = AES.new(key, AES.MODE_EAX)
        encrypted_response, tag = cipher.encrypt_and_digest(response)
        return b"%(nonce)s%(key)s%(tag)s%(data)s" % {
            b"nonce": cipher.nonce,
            b"key": key,
            b"tag": tag,
            b"data": encrypted_response
        }
    return wrapper
