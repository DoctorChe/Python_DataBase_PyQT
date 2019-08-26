import json
from client.utils.config_client import ENCODING, MSG_SIZE


def send_message(socket, msg):
    """
    Отправка сообщения
    :param socket: сокет
    :param msg: словарь сообщения
    :return: None
    """
    socket.send(json.dumps(msg).encode(ENCODING))


def recieve_message(socket):
    """
    Получение сообщения
    :param socket: сокет
    :return: словарь сообщения
    """
    # return json.loads(socket.recv(MSG_SIZE).decode(ENCODING))
    try:
        return json.loads(socket.recv(MSG_SIZE).decode(ENCODING))
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
