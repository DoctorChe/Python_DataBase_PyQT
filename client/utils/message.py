import json
import zlib

from client.utils.config_client import ENCODING, MSG_SIZE
from client.utils.errors import MessageIsNotDictError


def send_message(socket, msg: dict):
    """
    Отправка сообщения
    :param socket: сокет
    :param msg: словарь сообщения
    :return: None
    """
    if not isinstance(msg, dict):
        raise MessageIsNotDictError
    js_message = json.dumps(msg)
    encoded_message = js_message.encode(ENCODING)
    compressed_message = zlib.compress(encoded_message)
    socket.send(compressed_message)


def recieve_message(socket) -> dict:
    """
    Получение сообщения
    :param socket: сокет
    :return: словарь сообщения
    """
    try:
        compressed_message = socket.recv(MSG_SIZE)
        decompressed_message = zlib.decompress(compressed_message)
        decoded_message = decompressed_message.decode(ENCODING)
        message = json.loads(decoded_message)
    # except ConnectionAbortedError:
    #     return {
    #         "response": 499,
    #         "error": "Client Closed Request"
    #     }
    # except json.decoder.JSONDecodeError:
    #     print("Something wrong with JSON")
    except OSError:
        return {
            "response": 499,
            "error": "Client Closed Request"
        }
    else:
        return message
