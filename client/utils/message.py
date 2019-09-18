import json
import zlib
from functools import wraps

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from .config_client import ENCODING
from .util import get_chunk


def to_json_middleware(func):
    @wraps(func)
    def wrapper(sock, request, *args, **kwargs):
        encoded_request = json.dumps(request).encode(ENCODING)
        res = func(sock, encoded_request, *args, **kwargs)
        return res
    return wrapper


def from_json_middleware(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        b_request = func(*args, **kwargs)
        js_request = b_request.decode(ENCODING)
        request = json.loads(js_request)
        return request
    return wrapper


def encrypt_middleware(func):
    @wraps(func)
    def wrapper(sock, encoded_request, *args, **kwargs):
        key = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_EAX)
        encrypted_request, tag = cipher.encrypt_and_digest(encoded_request)

        encrypted_data = b"%(nonce)s%(key)s%(tag)s%(data)s" % {
            b"nonce": cipher.nonce,
            b"key": key,
            b"tag": tag,
            b"data": encrypted_request
        }
        res = func(sock, encrypted_data, *args, **kwargs)
        return res
    return wrapper


def decrypt_middleware(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        encrypted_request = func(*args, **kwargs)

        nonce, encrypted_request = get_chunk(encrypted_request, 16)
        key, encrypted_request = get_chunk(encrypted_request, 16)
        tag, encrypted_request = get_chunk(encrypted_request, 16)

        cipher = AES.new(key, AES.MODE_EAX, nonce)

        decrypted_request = cipher.decrypt_and_verify(encrypted_request, tag)
        return decrypted_request
    return wrapper


def compress_middleware(func):
    @wraps(func)
    def wrapper(sock, b_request, *args, **kwargs):
        compressed_b_request = zlib.compress(b_request)
        res = func(sock, compressed_b_request, *args, **kwargs)
        return res
    return wrapper


def decompress_middleware(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        compressed_b_request = func(*args, **kwargs)
        b_request = zlib.decompress(compressed_b_request)
        return b_request
    return wrapper
