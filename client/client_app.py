import threading
import time
from socket import socket, AF_INET, SOCK_STREAM

from client.utils.protocol import create_message
from jim.config_jim import (ACTION, TIME, TYPE, USER, ACCOUNT_NAME, STATUS, RESPONSE, PRESENCE, RESPONSE_CODES, MESSAGE,
                            OK, ERROR, ALERT, ACCEPTED, GET_CONTACTS)
from client.utils.message import send_message, recieve_message
from client.utils.parser import create_parser
from client.utils.metaclasses import ClientVerifier
from client.utils.errors import (ResponseCodeError, ResponseCodeLenError, MessageIsNotDictError, MandatoryKeyError)
from client.utils.descriptors import CheckedHost, ClientName

import logging
from client.utils import client_log_config
# from client.utils import client_log_config
from client.utils.decorators import Log

logger = logging.getLogger("client")
log = Log(logger)


# class Client(threading.Thread, metaclass=ClientVerifier):
class Client(metaclass=ClientVerifier):

    __name = ClientName()
    __host = CheckedHost()

    def __init__(self, host, transport, name="Guest"):
        self.__name = name
        self.__host = host
        self.__socket = transport
        # self.__socket = None

        # super().__init__()  # Конструктор предка

    def __enter__(self):
        if not self.__socket:
            # self.__socket = socket()
            raise TypeError("Socket does not exist")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        message = "Client shutdown"
        if exc_type:
            if exc_type is not KeyboardInterrupt:
                message = "Client stopped with error"
        logging.info(message)
        self.close()
        return True

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
        res = f"args: ({response},)- {response}"
        logger.info(f"{res} - {self.translate_message.__name__}")

        return response

    def read_messages(self):
        """
        Клиент читает входящие сообщения в бесконечном цикле
        """
        while True:
            message = self.recieve()  # получаем ответ от сервера
            if RESPONSE in message:
                if ERROR in message:
                    print(f"Ошибка {message[RESPONSE]} - {message[ERROR]}")
                if ALERT in message:
                    print(message[ALERT])
            # elif MESSAGE in message:
            if MESSAGE in message:
                print(message[MESSAGE])  # там должно быть сообщение

    def write_messages(self):
        """Клиент пишет сообщение в бесконечном цикле"""
        while True:
            message_str = input(">>> ")

            message_list = message_str.split()
            action = message_list[0]
            if len(message_list) > 1:
                text = " ".join(message_list[1:])
            else:
                text = ""
            message = create_message(action, text)
            self.send(message)

            # elif message_str == "help":
            #     print("message <получатель> <текст> - отправить сообщение")
            # elif message_str == "quit":
            #     try:
            #         send_message(self.__socket, create_exit_message(self.name))
            #         # self.send(self.create_exit_message())
            #     except:
            #         pass
            #     print("Завершение соединения.")
            #     logger.info("Завершение работы по команде пользователя.")
            #     time.sleep(0.5)  # Задержка неоходима, чтобы успело уйти сообщение о выходе
            #     break
            # else:
            #     print("Неверная команда, для справки введите help")

    def run(self):
        t = threading.Thread(target=self.read_messages)
        t.daemon = True
        t.start()
        self.write_messages()


def main():
    parser = create_parser()

    account_name = parser.parse_args().name
    print(account_name)
    # status = "Yep, I am here!"

    transport = socket(AF_INET, SOCK_STREAM)

    with Client(
            (parser.parse_args().addr, parser.parse_args().port),
            transport,
            account_name
    ) as client:
        if client.connect():
            message = create_message(PRESENCE, account_name)  # формируем presense сообщение
            client.send(message)  # отправляем сообщение серверу
            response = client.recieve()  # получаем ответ от сервера
            response = client.translate_message(response)  # разбираем сообщение от сервера
            if response[RESPONSE] == OK:
                print("Соединение установлено.")
                message = create_message(GET_CONTACTS, account_name)  # запрашиваем список контактов
                client.send(message)  # отправляем сообщение серверу
                response = client.recieve()  # получаем ответ от сервера
                response = client.translate_message(response)  # разбираем сообщение от сервера
                if response[RESPONSE] == ACCEPTED:
                    if ALERT in response:
                        print(f"Список контактов:\n{response[ALERT]}")
                    else:
                        print("Список контактов пуст")
                # print("Формат сообщения:\n"
                #       "message <получатель> <текст>")
                client.run()


if __name__ == "__main__":
    main()
