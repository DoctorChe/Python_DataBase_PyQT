import time
from socket import socket, AF_INET, SOCK_STREAM
from jim.config import (ACTION, TIME, TYPE, USER, ACCOUNT_NAME, STATUS, RESPONSE, PRESENCE, MSG, RESPONSE_CODES, TO,
                        FROM, MESSAGE, OK)
from jim.message import send_message, recieve_message
from utils.parser import create_parser
from errors import (ResponseCodeError, ResponseCodeLenError, MessageIsNotDictError, MandatoryKeyError,
                    UsernameToLongError)
from utils.decorators import Log

import logging
import log.client_log_config

logger = logging.getLogger("client")
log = Log(logger)


class Client:
    """Класс Клиент"""

    def __init__(self, host, name="Guest"):
        # self.__name = name
        self.__set_name(name)
        self.__host = host
        self.__socket = socket(AF_INET, SOCK_STREAM)

    # @property
    # def name(self):
    #     return self.__name
    #
    # @name.setter
    # def __name(self, value):
    #     if not isinstance(value, str):
    #         raise TypeError
    #     if len(value) > 25:
    #         raise UsernameToLongError(value)
    #     self.__name = value

    def get_name(self):
        return self.__name

    def __set_name(self, name):
        if not isinstance(name, str):
            raise TypeError
        if len(name) > 25:
            raise UsernameToLongError(name)
        self.__name = name

    name = property(get_name, __set_name)

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
            # print(message)
            print(message[MESSAGE])  # там должно быть сообщение всем

    def write_messages(self):
        """Клиент пишет сообщение в бесконечном цикле"""
        while True:
            text = input("Ваше сообщение: ")  # Вводим сообщение с клавиатуры
            message = self.create_message("#all", text)  # Создаем jim сообщение
            send_message(self.__socket, message)  # отправляем на сервер

    @staticmethod
    def create_message(message_to, text, account_name='Guest'):
        return {ACTION: MSG, TIME: time.time(), TO: message_to, FROM: account_name, MESSAGE: text}


def run():
    parser = create_parser()

    # account_name = "Doctor_Che"
    status = "Yep, I am here!"

    # client = Client((parser.parse_args().addr, parser.parse_args().port), account_name)
    client = Client((parser.parse_args().addr, parser.parse_args().port))
    if client.connect():
        msg = client.create_presence(status)  # формируем presence-сообщение
        client.send(msg)  # отправляем сообщение серверу
        response = client.recieve()  # получаем ответ от сервера
        response = client.translate_message(response)  # разбираем сообщение от сервера
        # print(response)
        if response["response"] == OK:
            print("Соединение установлено.")
            if parser.parse_args().mode == "r":
                client.read_messages()
            elif parser.parse_args().mode == "w":
                client.write_messages()
            else:
                raise Exception("Не верный режим чтения/записи.")

        client.close()


if __name__ == "__main__":
    run()
