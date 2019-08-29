import select
import threading
from typing import Tuple
from socket import socket, AF_INET, SOCK_STREAM
from jim.config_jim import TO
from server.utils.config_server import WORKERS
from server.utils.hendlers import handle_process_client_message
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
        self.__server = None
        self.clients = []  # список подключенных клиентов
        self.names = None  # Словарь содержащий имена и соответствующие им сокеты
        self.messages = []  # Список сообщений на отправку
        self.database = database  # База данных сервера

        # super().__init__()  # Конструктор предка

    def __enter__(self):
        # if not self.__server:
        #     self.__server = socket(AF_INET, SOCK_STREAM)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        message = "Server shutdown"
        if exc_type:
            if exc_type is not KeyboardInterrupt:
                message = "Server stopped with error"
        logging.info(message)
        return True

    def __new_listen_socket(self):
        transport = socket(AF_INET, SOCK_STREAM)
        transport.bind(self.__host)
        transport.settimeout(0.5)

        # Начинаем слушать сокет
        self.__server = transport
        self.__server.listen(WORKERS)

    def accept(self):
        # Ждём подключения, если таймаут вышел, ловим исключение
        try:
            client, client_address = self.__server.accept()
        except OSError:
            pass  # timeout вышел
        else:
            self.clients.append(client)
            logger.info(f"Установлено соедение с клиентом {client_address}")
            print(f"Установлено соедение с клиентом {str(client_address)}")

    def read(self, sock):
        try:
            message = recieve_message(sock)
            # print(f"Принято сообщение: {message}")
        except Exception:
            logger.info(f"Клиент {sock.getpeername()} отключился от сервера.")
            self.clients.remove(sock)
        else:
            if message:
                # self.handle_process_client_message(message, sock)
                # TODO: перенести разбор сообщения в метод run
                self.messages.append(message)
                # print(f"Сообщение: {message} добавлено в список сообщений")

    # def write(self, send_data_lst, message):
    def write(self, sock, message):
        try:
            # self.process_message(message, send_data_lst)
            # TODO: сделать проверку: зарегистрирован ли клиент на сервере
            # print(f"Отсылка сообщения: {message} Клиенту: {sock}")
            send_message(sock, message)
            # print(f"Сообщение: {message} отослано клиенту: {sock}")
        except TypeError:
            logger.info(f"Связь с клиентом с именем {message[TO]} была потеряна")
            try:
                self.clients.remove(self.names[message[TO]])
            except ValueError:
                pass
            del self.names[message[TO]]

    def run(self):
        self.__new_listen_socket()  # Инициализация сокета

        print("Сервер запущен")

        if self.names is None:
            self.names = dict()

        # Основной цикл программы сервера
        while True:
            self.accept()

            # Проверить наличие событий ввода-вывода без таймаута
            wait = 0
            recv_data_list = []
            send_data_list = []
            err_list = []
            try:
                if self.clients:
                    recv_data_list, send_data_list, err_list = select.select(self.clients, self.clients, [], wait)
            except OSError:
                # Исключение произойдёт, если какой-то клиент отключится
                pass

            # Принимаем сообщения и если ошибка, исключаем клиента
            if recv_data_list:
                for client_with_message in recv_data_list:
                    # self.read(client_with_message)
                    r_thread = threading.Thread(
                        target=self.read, args=(client_with_message, )
                    )
                    r_thread.start()

            # Если есть сообщения, обрабатываем каждое
            if self.messages:
                # for message in self.messages:
                message = self.messages.pop()
                # print(f"Сообщение: {message} извлечено из списка сообщений")
                response = handle_process_client_message(message, self.database)
                # print(f"Сформирован ответ: {response} на сообщение {message}")
                for client_waiting_message in send_data_list:
                    # self.write(send_data_list, message)
                    # self.write(client_waiting_message, response)
                    w_thread = threading.Thread(
                        # target=self.write, args=(send_data_list, message)
                        target=self.write, args=(client_waiting_message, response)
                    )
                    w_thread.start()
                # self.messages.clear()

    # Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение, список зарегистрированых
    # пользователей и слушающие сокеты. Ничего не возвращает.
    # def process_message(self, message: dict, listen_socks: list):
    #     if (
    #             message[TO] in self.names and
    #             self.names[message[TO]] in listen_socks
    #     ):
    #         send_message(self.names[message[TO]], message)
    #         logger.info(f"Отправлено сообщение пользователю {message[TO]} от пользователя {message[FROM]}.")
    #     elif (
    #             message[TO] in self.names and
    #             self.names[message[TO]] not in listen_socks
    #     ):
    #         raise ConnectionError
    #     else:
    #         logger.error(
    #             f"Пользователь {message[TO]} не зарегистрирован на сервере, отправка сообщения невозможна.")


def main():
    parser = create_parser()

    database = ServerStorage()  # Инициализация базы данных

    with Server((parser.parse_args().addr, parser.parse_args().port), database) as server:
        server.run()
        # server.daemon = True
        # server.start()


if __name__ == "__main__":
    main()
