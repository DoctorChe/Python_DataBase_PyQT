import json
import zlib

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from utils.config_client import ENCODING, MSG_SIZE
from utils.util import get_chunk

from client.utils.decorators import logged


@logged
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
