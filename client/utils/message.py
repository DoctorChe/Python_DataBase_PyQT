import json
import zlib
from functools import wraps

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from utils.config_client import ENCODING, MSG_SIZE
from utils.util import get_chunk

from client.utils.decorators import logged


def to_json_middleware(func):
    @wraps(func)
    def wrapper(sock, request, *args, **kwargs):
        print(f"request = {request}")
        js_request = json.dumps(request)
        print(f"js_request = {js_request}")
        res = func(sock, js_request, *args, **kwargs)
        return res
    return wrapper


def from_json_middleware(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        js_request = func(*args, **kwargs)
        print(f"js_request = {js_request}")
        request = json.loads(js_request)
        print(f"request = {request}")
        return request
    return wrapper


def encrypt_middleware(func):
    @wraps(func)
    def wrapper(sock, encoded_message, *args, **kwargs):
        key = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_EAX)
        encrypted_message, tag = cipher.encrypt_and_digest(encoded_message)

        encrypted_string = b"%(nonce)s%(key)s%(tag)s%(data)s" % {
            b"nonce": cipher.nonce,
            b"key": key,
            b"tag": tag,
            b"data": encrypted_message
        }
        res = func(sock, encrypted_string, *args, **kwargs)
        return res
    return wrapper


def decrypt_middleware(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        encrypted_string = func(*args, **kwargs)

        nonce, encrypted_message = get_chunk(encrypted_string, 16)
        key, encrypted_message = get_chunk(encrypted_string, 16)
        tag, encrypted_message = get_chunk(encrypted_string, 16)

        cipher = AES.new(key, AES.MODE_EAX, nonce)

        decrypted_message = cipher.decrypt_and_verify(encrypted_message, tag)
        return decrypted_message
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
        b_request = zlib.compress(compressed_b_request)
        return b_request
    return wrapper


@logged
# @compress_middleware
# @encrypt_middleware
@to_json_middleware
def send_message(socket, msg: dict):
    """
    Отправка сообщения
    :param socket: сокет
    :param msg: словарь сообщения
    :return: None
    """
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_EAX)

    encoded_message = json.dumps(msg).encode(ENCODING)

    encrypted_message, tag = cipher.encrypt_and_digest(encoded_message)

    compressed_message = zlib.compress(b"%(nonce)s%(key)s%(tag)s%(data)s" % {
        b"nonce": cipher.nonce,
        b"key": key,
        b"tag": tag,
        b"data": encrypted_message
        })

    socket.send(compressed_message)


@logged
def receive_message(socket) -> dict:
    """
    Получение сообщения
    :param socket: сокет
    :return: словарь сообщения
    """
    try:
        compressed_message = socket.recv(MSG_SIZE)
        encrypted_message = zlib.decompress(compressed_message)

        nonce, encrypted_message = get_chunk(encrypted_message, 16)
        key, encrypted_message = get_chunk(encrypted_message, 16)
        tag, encrypted_message = get_chunk(encrypted_message, 16)

        cipher = AES.new(key, AES.MODE_EAX, nonce)

        decrypted_message = cipher.decrypt_and_verify(encrypted_message, tag)
        message = json.loads(decrypted_message.decode(ENCODING))
    except OSError:
        pass
        # return {
        #     "response": 499,
        #     "error": "Client Closed Request"
        # }
    else:
        return message
