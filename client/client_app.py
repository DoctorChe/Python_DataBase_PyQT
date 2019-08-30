import threading
import time

from client.utils.protocol import create_message
from jim.config_jim import (ACTION, TIME, TYPE, USER, ACCOUNT_NAME, STATUS, RESPONSE, PRESENCE, RESPONSE_CODES, MESSAGE,
                            ERROR, ALERT)
from client.utils.message import send_message, recieve_message
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

    _name = ClientName()
    _host = CheckedHost()

    def __init__(self, host, transport, name="Guest"):
        self._name = name
        self._host = host
        self._socket = transport
        # self._socket = None

        # super().__init__()  # Конструктор предка

    def __enter__(self):
        if not self._socket:
            # self._socket = socket()
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
        return self._name

    @log
    def connect(self):
        try:
            self._socket.connect(self._host)
        except ConnectionRefusedError:
            # print("Connection refused. Server unavailable.")

            # Заполняем лог
            # res = "Connection refused. Server unavailable."
            # logger.error(f"{res} - {self.connect.__name__}")

            return False
        return True

    def close(self):
        self._socket.close()

    def send(self, request):
        send_message(self._socket, request)

    def recieve(self):
        return recieve_message(self._socket)

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
            #         send_message(self._socket, create_exit_message(self.name))
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
