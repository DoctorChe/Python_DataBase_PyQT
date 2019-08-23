import select
from typing import Tuple
from socket import socket, AF_INET, SOCK_STREAM
from jim.config_jim import (ACTION, TIME, PRESENCE, RESPONSE, ERROR, MSG, TO, FROM, USER, ACCOUNT_NAME, MESSAGE, QUIT,
                            RESPONSE_CODES, WRONG_REQUEST, CONFLICT, OK, NOT_FOUND)
from server.utils.config_server import WORKERS
from server.utils.message import send_message, recieve_message
from server.utils.server_db import ServerStorage
from server.utils.parser import create_parser
from server.utils.metaclasses import ServerVerifier
from server.utils.descriptors import CheckedHost

import logging
# from server.utils import server_log_config
from server.utils import server_log_config
from server.utils.decorators import Log

logger = logging.getLogger("server")
log = Log(logger)


# class Server(threading.Thread, metaclass=ServerVerifier):
class Server(metaclass=ServerVerifier):

    __host = CheckedHost()

    def __init__(self, host: Tuple[str, int], database):
        self.__host = host

        self.clients = []  # список подключенных клиентов
        self.names = None  # Словарь содержащий имена и соответствующие им сокеты

        self.messages = []  # Список сообщений на отправку

        self.database = database  # База данных сервера

        # super().__init__()  # Конструктор предка

    def __new_listen_socket(self):
        transport = socket(AF_INET, SOCK_STREAM)
        transport.bind(self.__host)
        transport.listen(WORKERS)
        transport.settimeout(0.5)
        # Таймаут необходим, чтобы выполнять разные действия с сокетом:
        # - проверить сокет на наличие подключений новых клиентов
        # - проверить сокет на наличие данных

        # Начинаем слушать сокет
        self.__server = transport
        self.__server.listen()

    # def run(self):
    def listen(self):
        self.__new_listen_socket()  # Инициализация сокета

        print("Сервер запущен")

        if self.names is None:
            self.names = dict()

        # Основной цикл программы сервера
        while True:
            # Ждём подключения, если таймаут вышел, ловим исключение
            try:
                client, client_address = self.__server.accept()
            except OSError:
                pass  # timeout вышел
            else:
                self.clients.append(client)
                logger.info(f"Установлено соедение с клиентом {client_address}")
                print(f"Установлено соедение с клиентом {str(client_address)}")

            # Проверить наличие событий ввода-вывода без таймаута
            wait = 0
            recv_data_lst = []
            send_data_lst = []
            err_lst = []
            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], wait)
            except OSError:
                # Исключение произойдёт, если какой-то клиент отключится
                pass

            # Принимаем сообщения и если ошибка, исключаем клиента
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(recieve_message(client_with_message), client_with_message)
                    except:
                        logger.info(f"Клиент {client_with_message.getpeername()} отключился от сервера.")
                        self.clients.remove(client_with_message)

            # Если есть сообщения, обрабатываем каждое
            for message in self.messages:
                # self.process_message(message, send_data_lst)
                try:
                    self.process_message(message, send_data_lst)
                # except:
                except TypeError:
                    logger.info(f"Связь с клиентом с именем {message[TO]} была потеряна")
                    try:
                        self.clients.remove(self.names[message[TO]])
                    except ValueError:
                        pass
                    del self.names[message[TO]]
            self.messages.clear()

    # Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение, список зарегистрированых
    # пользователей и слушающие сокеты. Ничего не возвращает.
    def process_message(self, message: dict, listen_socks: list):
        if (
                message[TO] in self.names and
                self.names[message[TO]] in listen_socks
        ):
            send_message(self.names[message[TO]], message)
            logger.info(f"Отправлено сообщение пользователю {message[TO]} от пользователя {message[FROM]}.")
        elif (
                message[TO] in self.names and
                self.names[message[TO]] not in listen_socks
        ):
            raise ConnectionError
        else:
            logger.error(
                f"Пользователь {message[TO]} не зарегистрирован на сервере, отправка сообщения невозможна.")

    # Обработчик сообщений от клиентов, принимает словарь - сообщение от клиента, проверяет корректность, отправляет
    #     словарь-ответ в случае необходимости.
    def process_client_message(self, message: dict, client: socket):
        logger.debug(f"Разбор сообщения от клиента : {message}")
        # Если это сообщение о присутствии, принимаем и отвечаем
        if (
                self.common_check_message(message) and
                message[ACTION] == PRESENCE and
                USER in message
        ):
            # Если такой пользователь ещё не зарегистрирован, регистрируем,
            # иначе отправляем ответ и завершаем соединение.
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(message[USER][ACCOUNT_NAME], client_ip, client_port)
                response = self.create_responce(OK)
                send_message(client, response)
            else:
                response = self.create_responce(CONFLICT, "Имя пользователя уже занято.")
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
        elif (
                self.common_check_message(message) and
                message[ACTION] == MSG and
                TO in message and
                FROM in message and
                MESSAGE in message
        ):
            if message[TO] in self.names.keys():
                if message[TO] == message[FROM]:
                    response = self.create_responce(NOT_FOUND, "Попытка отправки сообщения самому себе")
                    print(f"Попытка отправки сообщения самому себе ({message[TO]})")
                    send_message(client, response)
                else:
                    self.messages.append(message)
            else:
                response = self.create_responce(NOT_FOUND, "Получатель сообщения не найден")
                print(f"Не найден клиент с именем {message[TO]}")
                send_message(client, response)
            return
        # Если клиент выходит
        elif (
                self.common_check_message(message) and
                message[ACTION] == QUIT and
                ACCOUNT_NAME in message
        ):
            self.database.user_logout(message[ACCOUNT_NAME])
            print(f"Клиент {message[ACCOUNT_NAME].fileno()} {message[ACCOUNT_NAME].getpeername()} отключился")
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            return
        # Иначе отдаём Bad request
        else:
            response = self.create_responce(WRONG_REQUEST, "Запрос некорректен.")
            send_message(client, response)
            return

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
    def create_responce(self, responce: int, error=None) -> dict:
        """
        Формирование ответа клиенту
        :param responce: код ответа
        :param error: текст ошибки
        :return: словарь ответа
        """

        if isinstance(error, str):
            if responce in RESPONSE_CODES:
                return {
                    RESPONSE: responce,
                    ERROR: error
                }
        else:
            return {
                RESPONSE: responce
            }


def run():
    parser = create_parser()

    database = ServerStorage()  # Инициализация базы данных

    server = Server((parser.parse_args().addr, parser.parse_args().port), database)
    server.listen()
    # server.daemon = True
    # server.start()


if __name__ == "__main__":
    run()