import threading
import time
from socket import socket, AF_INET, SOCK_STREAM
from jim.config import (ACTION, TIME, TYPE, USER, ACCOUNT_NAME, STATUS, RESPONSE, PRESENCE, MSG, RESPONSE_CODES, TO,
                        FROM, MESSAGE, OK)
from jim.message import send_message, recieve_message
from utils.parser import create_parser
from errors import (ResponseCodeError, ResponseCodeLenError, MessageIsNotDictError, MandatoryKeyError)
from utils.decorators import Log
from utils.descriptors import CheckedHost, ClientName
from utils.metaclasses import ClientVerifier

import logging
import log.client_log_config

logger = logging.getLogger("client")
log = Log(logger)


class Client(metaclass=ClientVerifier):

    __name = ClientName()
    __host = CheckedHost()

    def __init__(self, host, transport, name="Guest"):
        self.__name = name
        self.__host = host
        self.__socket = transport

    @property
    def name(self):
        return self.__name

    @log
    def connect(self):
        try:
            self.__socket.connect(self.__host)
        except ConnectionRefusedError:
            # print("Connection refused. Server unavailable.")

            # Заполняем лог
            # res = "Connection refused. Server unavailable."
            # logger.error(f"{res} - {self.connect.__name__}")

            return False
        return True

    def close(self):
        self.__socket.close()

    def send(self, request):
        send_message(self.__socket, request)

    def recieve(self):
        return recieve_message(self.__socket)

    @log
    def create_presence(self, status=None):
        """
        Создание ​​presence-сообщения
        :param status: статус пользователя
        :return: словарь сообщения
        """

        unix_timestamp = time.time()
        presence = {
            ACTION: PRESENCE,
            TIME: unix_timestamp,
            USER: {
                ACCOUNT_NAME: self.name,
            }
        }
        if status:
            presence[TYPE] = "status"
            presence[USER][STATUS] = status

        # Заполняем лог
        # res = f"- {presence}"
        # logger.info(f"{res} - {self.create_presence.__name__}")

        return presence

    @log
    def translate_message(self, response):
        """
        Разбор сообщения
        :param response: словарь ответа от сервера
        :return: корректный словарь ответа
        """

        if not isinstance(response, dict):
            raise MessageIsNotDictError  # ошибка неверный формат сообщения

        if RESPONSE not in response:
            raise MandatoryKeyError(RESPONSE)  # ошибка нужен обязательный ключ

        code = response[RESPONSE]

        if len(str(code)) != 3:  # длина кода не 3 символа
            raise ResponseCodeLenError(code)  # Ошибка неверная длина кода ошибки

        if code not in RESPONSE_CODES:
            raise ResponseCodeError(code)  # ошибка неверный код ответа

        # Заполняем лог
        # res = f"args: ({response},)- {response}"
        # logger.info(f"{res} - {self.translate_message.__name__}")

        return response

    def read_messages(self):
        """
        Клиент читает входящие сообщения в бесконечном цикле
        :param client: сокет клиента
        """
        while True:
            message = recieve_message(self.__socket)  # читаем сообщение
            print(message[MESSAGE])  # там должно быть сообщение всем

    def write_messages(self):
        """Клиент пишет сообщение в бесконечном цикле"""
        while True:
            message_str = input(">>> ")
            if message_str.startswith("message"):
                message_list = message_str.split()
                try:
                    to = message_list[1]
                    text = ' '.join(message_list[2:])
                except IndexError:
                    print("Не задан получатель или текст сообщения")
                else:
                    message = self.create_message(to, text)
                    self.send(message)
            elif message_str == "help":
                print("message <получатель> <текст> - отправить сообщение")
            elif message_str == "exit":
                break
            else:
                print("Неверная команда, для справки введите help")

    def create_message(self, message_to, text):
        return {
            ACTION: MSG,
            TIME: time.time(),
            TO: message_to,
            FROM: self.__name,
            MESSAGE: text
        }


def run():
    parser = create_parser()

    account_name = parser.parse_args().name
    print(account_name)
    status = "Yep, I am here!"

    transport = socket(AF_INET, SOCK_STREAM)
    client = Client((parser.parse_args().addr, parser.parse_args().port), transport, account_name)
    if client.connect():
        msg = client.create_presence(status)  # формируем presence-сообщение
        client.send(msg)  # отправляем сообщение серверу
        response = client.recieve()  # получаем ответ от сервера
        response = client.translate_message(response)  # разбираем сообщение от сервера
        if response["response"] == OK:
            print("Соединение установлено.")
            print("Формат сообщения:\n"
                  "message <получатель> <текст>")
            t = threading.Thread(target=client.read_messages)
            t.start()
            client.write_messages()
            # client.disconnect()

        client.close()


if __name__ == "__main__":
    run()
