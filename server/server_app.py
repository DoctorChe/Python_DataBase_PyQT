import select
import threading
from typing import Tuple
from socket import socket, AF_INET, SOCK_STREAM
from jim.config_jim import (
    ACTION, PRESENCE, MSG, TO, FROM, USER, ACCOUNT_NAME, MESSAGE, QUIT, WRONG_REQUEST, CONFLICT, OK, NOT_FOUND,
    GET_CONTACTS, ACCEPTED, ADD_CONTACT, DEL_CONTACT, UPDATE_CONTACT, GET_CONTACT,
    INFO)
from server.utils.config_server import WORKERS
from server.utils.message import send_message, recieve_message
from server.utils.protocol import common_check_message, create_response, create_alert_response
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
        except Exception:
            logger.info(f"Клиент {sock.getpeername()} отключился от сервера.")
            self.clients.remove(sock)
        else:
            if message:
                self.process_client_message(message, sock)
                # TODO: перенести разбор сообщения в метод run
                # self.messages.append(message)

    def write(self, send_data_lst, message):
        try:
            self.process_message(message, send_data_lst)
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
                    self.read(client_with_message)
                    # r_thread = threading.Thread(
                    #     target=self.read, args=(client_with_message, )
                    # )
                    # r_thread.start()

            # Если есть сообщения, обрабатываем каждое
            if self.messages:
                for message in self.messages:
                    # response = self.process_client_message(message, sock)
                    # self.write(send_data_list, message)
                    w_thread = threading.Thread(
                        target=self.write, args=(send_data_list, message)
                    )
                    w_thread.start()
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
        if common_check_message(message):
            if (
                    message[ACTION] == PRESENCE and
                    USER in message
            ):
                # Если такой пользователь ещё не зарегистрирован, регистрируем,
                # иначе отправляем ответ и завершаем соединение.
                if message[USER][ACCOUNT_NAME] not in self.names.keys():
                    self.names[message[USER][ACCOUNT_NAME]] = client
                    client_ip, client_port = client.getpeername()
                    self.database.user_login(message[USER][ACCOUNT_NAME], client_ip, client_port)
                    response = create_response(OK)
                    send_message(client, response)
                else:
                    response = create_response(CONFLICT, "Имя пользователя уже занято.")
                    send_message(client, response)
                    self.clients.remove(client)
                    client.close()
                return
            # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
            elif (
                    message[ACTION] == MSG and
                    TO in message and
                    FROM in message and
                    MESSAGE in message
            ):
                if message[TO] in self.names.keys():
                    if message[TO] == message[FROM]:
                        response = create_response(NOT_FOUND, "Попытка отправки сообщения самому себе")
                        print(f"Попытка отправки сообщения самому себе ('{message[TO]}')")
                        send_message(client, response)
                    else:
                        self.messages.append(message)
                else:
                    response = create_response(NOT_FOUND, "Получатель сообщения не найден")
                    print(f"Не найден клиент с именем '{message[TO]}'")
                    send_message(client, response)
                return
            # Если клиент выходит
            elif (
                    message[ACTION] == QUIT and
                    ACCOUNT_NAME in message
            ):
                self.database.user_logout(message[ACCOUNT_NAME])
                print(f"Клиент '{message[ACCOUNT_NAME].fileno()} {message[ACCOUNT_NAME].getpeername()}' отключился")
                self.clients.remove(self.names[message[ACCOUNT_NAME]])
                self.names[message[ACCOUNT_NAME]].close()
                del self.names[message[ACCOUNT_NAME]]
                return
            # Если клиент запрашивает список контактов
            elif (
                    message[ACTION] == GET_CONTACTS and
                    ACCOUNT_NAME in message
            ):
                print(f"Запрос списка контактов от клиента '{message[ACCOUNT_NAME]}'")
                contact_list = self.database.get_contacts(message[ACCOUNT_NAME])
                response = create_alert_response(ACCEPTED, str(contact_list))
                send_message(client, response)
                return
            # Если клиент запрашивает информацию о контакте из списка контактов
            elif (
                    message[ACTION] == GET_CONTACT and
                    ACCOUNT_NAME in message and
                    TO in message
            ):
                print(f"Запрос информации о контакте '{message[TO]}' "
                      f"из списка контактов от клиента '{message[ACCOUNT_NAME]}'")
                contact = self.database.get_contact(message[ACCOUNT_NAME], message[TO])
                response = create_alert_response(ACCEPTED, contact.information)
                send_message(client, response)
                return
            # Если клиент пытается добавить контакт в список контактов
            elif (
                    message[ACTION] == ADD_CONTACT and
                    ACCOUNT_NAME in message and
                    TO in message
            ):
                print(f"Запрос на добавление контакта '{message[TO]}' "
                      f"в список контактов от клиента '{message[ACCOUNT_NAME]}'")
                self.database.add_contact(message[ACCOUNT_NAME], message[TO])
                response = create_alert_response(ACCEPTED, "Contact added")
                send_message(client, response)
                return
            # Если клиент пытается удалить контакт из списка контактов
            elif (
                    message[ACTION] == DEL_CONTACT and
                    ACCOUNT_NAME in message and
                    TO in message
            ):
                print(f"Запрос на удаление контакта '{message[TO]}' "
                      f"из списка контактов от клиента '{message[ACCOUNT_NAME]}'")
                self.database.remove_contact(message[ACCOUNT_NAME], message[TO])
                response = create_alert_response(ACCEPTED, "Contact removed")
                send_message(client, response)
                return
            # Если клиент пытается обновить контакт в списке контактов
            elif (
                    message[ACTION] == UPDATE_CONTACT and
                    ACCOUNT_NAME in message and
                    TO in message and
                    INFO in message
            ):
                print(f"Запрос на удаление контакта '{message[TO]}' "
                      f"из списка контактов от клиента '{message[ACCOUNT_NAME]}'")
                self.database.update_contact(message[ACCOUNT_NAME], message[TO], message[INFO])
                response = create_alert_response(ACCEPTED, "Contact updated")
                send_message(client, response)
                return
        # Иначе отдаём Bad request
        else:
            response = create_response(WRONG_REQUEST, "Запрос некорректен.")
            send_message(client, response)
            return


def main():
    parser = create_parser()

    database = ServerStorage()  # Инициализация базы данных

    with Server((parser.parse_args().addr, parser.parse_args().port), database) as server:
        server.run()
        # server.daemon = True
        # server.start()


if __name__ == "__main__":
    main()
