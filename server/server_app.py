import select
import threading
from typing import Tuple
from socket import socket, AF_INET, SOCK_STREAM

from utils.config_jim import TO
from utils.config_server import WORKERS, MSG_SIZE
from utils.metaclasses import ServerVerifier
from utils.descriptors import CheckedHost

from utils.config_log_server import server_logger


# class Server(threading.Thread, metaclass=ServerVerifier):
class Server(metaclass=ServerVerifier):

    _host = CheckedHost()

    def __init__(self, host: Tuple[str, int], handler):
        self._host = host
        self._server = None
        self._clients = []  # список подключенных клиентов
        # self.names = None  # Словарь содержащий имена и соответствующие им сокеты
        self._messages = []  # Список сообщений на отправку
        self._handler = handler

        # super().__init__()  # Конструктор предка

    def __enter__(self):
        # if not self._server:
        #     self._server = socket(AF_INET, SOCK_STREAM)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        message = "Server shutdown"
        if exc_type:
            if exc_type is not KeyboardInterrupt:
                message = "Server stopped with error"
        server_logger.info(message)
        return True

    def __new_listen_socket(self):
        transport = socket(AF_INET, SOCK_STREAM)
        transport.bind(self._host)
        transport.settimeout(0.5)

        # Начинаем слушать сокет
        self._server = transport
        self._server.listen(WORKERS)

    def accept(self):
        # Ждём подключения, если таймаут вышел, ловим исключение
        try:
            client, client_address = self._server.accept()
        except OSError:
            pass  # timeout вышел
        else:
            self._clients.append(client)
            server_logger.info(f"Установлено соедение с клиентом {client_address}")

    def read(self, sock):
        try:
            message = sock.recv(MSG_SIZE)
        except Exception:
            server_logger.info(f"Клиент {sock.getpeername()} отключился от сервера.")
            self._clients.remove(sock)
        else:
            if message:
                self._messages.append(message)

    # def write(self, send_data_lst, message):
    def write(self, sock, message):
        try:
            # self.process_message(message, send_data_lst)
            # TODO: сделать проверку: зарегистрирован ли клиент на сервере
            sock.send(message)
        except TypeError:
            server_logger.info(f"Связь с клиентом с именем {message[TO]} была потеряна")
            try:
                # self._clients.remove(self.names[message[TO]])
                self._clients.remove(sock)
            except ValueError:
                pass
            # del self.names[message[TO]]

    def run(self):
        self.__new_listen_socket()  # Инициализация сокета

        server_logger.info("Сервер запущен")

        # if self.names is None:
        #     self.names = dict()

        # Основной цикл программы сервера
        while True:
            self.accept()

            # Проверить наличие событий ввода-вывода без таймаута
            wait = 0
            recv_data_list = []
            send_data_list = []
            err_list = []
            try:
                if self._clients:
                    recv_data_list, send_data_list, err_list = select.select(self._clients, self._clients, [], wait)
            except OSError:
                # Исключение произойдёт, если какой-то клиент отключится
                pass

            # Принимаем сообщения и если ошибка, исключаем клиента
            if recv_data_list:
                for client_with_message in recv_data_list:
                    r_thread = threading.Thread(
                        target=self.read, args=(client_with_message, )
                    )
                    r_thread.start()

            # Если есть сообщения, обрабатываем каждое
            if self._messages:
                message = self._messages.pop()
                response = self._handler(message)
                for client_waiting_message in send_data_list:
                    w_thread = threading.Thread(
                        target=self.write, args=(client_waiting_message, response)
                    )
                    w_thread.start()

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
