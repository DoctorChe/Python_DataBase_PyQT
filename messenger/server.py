import select
from typing import Tuple
from socket import socket, AF_INET, SOCK_STREAM
from jim.config import ACTION, TIME, PRESENCE, RESPONSE, ERROR
from jim.config import WORKERS
from jim.message import send_message, recieve_message
from utils.parser import create_parser
from utils.decorators import Log

import logging
import log.server_log_config

logger = logging.getLogger("server")
log = Log(logger)


class Server:
    """Класс Сервер"""

    def __init__(self, host: Tuple[str, int]):
        self.__host = host
        self.__new_listen_socket()

    def __new_listen_socket(self):
        self.__server = socket(AF_INET, SOCK_STREAM)
        self.__server.bind(self.__host)
        self.__server.listen(WORKERS)
        self.__server.settimeout(0.2)  # Таймаут для операций с сокетом
        # Таймаут необходим, чтобы выполнять разные действия с сокетом:
        # - проверить сокет на наличие подключений новых клиентов
        # - проверить сокет на наличие данных

    def listen(self):
        clients = []  # список объектов клиентских сокетов
        while True:
            try:
                client, addr = self.__server.accept()
                presence = recieve_message(client)  # принимаем сообщение от клиента
                response = self.create_responce(presence)  # формируем ответ клиенту
                send_message(client, response)  # отправляем ответ клиенту
            except OSError as e:
                pass  # timeout вышел
            else:
                print(f"Получен запрос на соединение с {str(addr)}")
                clients.append(client)
                print(f"clients = {clients}")
            finally:
                # Проверить наличие событий ввода-вывода без таймаута
                wait = 0
                r = []
                w = []
            try:
                r, w, e = select.select(clients, clients, [], wait)
            except Exception as e:
                # Исключение произойдёт, если какой-то клиент отключится
                pass  # Ничего не делать, если какой-то клиент отключился
                # Обойти список клиентов, читающих из сокета
            msgs = self.read_messages(r, clients)  # принимаем сообщение от всех клиентов
            if msgs:
                print(f"Получены сообщения\n{msgs}")
                self.write_messages(msgs, w, clients)

    @staticmethod
    def common_check_message(msg: dict) -> bool:
        """
        Базовая проверка сообщения
        :param msg: словарь сообщения
        :return: результат проверки
        """

        def check_length(msg: dict) -> bool:
            if len(str(msg)) <= 640:
                return True
            return False

        def check_action(msg: dict) -> bool:
            if ACTION in msg and len(msg[ACTION]) <= 15:
                return True
            return False

        def check_time(msg: dict) -> bool:
            if TIME in msg and isinstance(msg[TIME], float):
                return True
            return False

        if check_length(msg) and check_action(msg) and check_time(msg):
            return True
        return False

    @log
    def create_responce(self, msg: dict) -> dict:
        """
        Формирование ответа клиенту
        :param msg: словарь presence запроса
        :return: словарь ответа
        """

        if self.common_check_message(msg) and msg[ACTION] == PRESENCE:
            response = {
                RESPONSE: 200
            }

            return response
        else:
            response = {
                RESPONSE: 400,
                ERROR: "Неправильный запрос/JSON объект"
            }

            return response

    @staticmethod
    def read_messages(r_clients, all_clients):
        """Чтение запросов из списка клиентов
        :param r_clients: клиенты которые могут отправлять сообщения
        :param all_clients: все клиенты
        :return:
        """

        # messages = {}      # Словарь сообщений вида {сокет: сообщение}
        messages = []
        for sock in r_clients:
            try:
                # messages[sock] = recieve_message(sock)  # Получаем входящие сообщения
                message = recieve_message(sock)  # Получаем входящие сообщения
                messages.append(message)  # Добавляем их в список
                # В идеале нам нужно сделать еще проверку, что сообщение нужного формата прежде чем его пересылать!
            except Exception:
                print(f"Клиент {sock.fileno()} {sock.getpeername()} отключился")
                all_clients.remove(sock)

        return messages  # Возвращаем список сообщений

    @staticmethod
    def write_messages(messages, w_clients, all_clients):
        """Эхо-ответ сервера клиентам, от которых были запросы
        :param requests: словарь сообщений
        :param w_clients: клиенты которые читают
        :param all_clients: все клиенты
        """
        for sock in w_clients:
            # if sock in requests:
            for message in messages:
                try:
                    send_message(sock, message)  # Отправить на тот сокет, который ожидает отправки
                except Exception:  # Сокет недоступен, клиент отключился
                    print(f"Клиент {sock.fileno()} {sock.getpeername()} отключился")
                    sock.close()
                    all_clients.remove(sock)


def run():
    parser = create_parser(True)

    server = Server((parser.parse_args().addr, parser.parse_args().port))
    server.listen()


if __name__ == "__main__":
    run()
