import threading

from utils.protocol import create_message
from utils.config_jim import RESPONSE, RESPONSE_CODES, MESSAGE, DATA
from utils.message import send_message, receive_message
from utils.metaclasses import ClientVerifier
from utils.errors import (ResponseCodeError, ResponseCodeLenError, MessageIsNotDictError, MandatoryKeyError)
from utils.descriptors import CheckedHost, ClientName

from client.utils.config_log_client import client_logger
from client.utils.decorators import logged


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
        client_logger.info(message)
        self.close()
        return True

    @property
    def name(self):
        return self._name

    @logged
    def connect(self):
        try:
            self._socket.connect(self._host)
        except ConnectionRefusedError:
            # print("Connection refused. Server unavailable.")
            return False
        return True

    def close(self):
        self._socket.close()

    def send(self, request):
        send_message(self._socket, request)

    def receive(self):
        return receive_message(self._socket)

    # @logged
    # def create_presence(self, status=None):
    #     """
    #     Создание ​​presence-сообщения
    #     :param status: статус пользователя
    #     :return: словарь сообщения
    #     """
    #
    #     unix_timestamp = time.time()
    #     presence = {
    #         ACTION: PRESENCE,
    #         TIME: unix_timestamp,
    #         USER: {
    #             ACCOUNT_NAME: self.name,
    #         }
    #     }
    #     # if status:
    #     #     presence[TYPE] = "status"
    #     #     presence[USER][STATUS] = status
    #
    #     return presence

    @logged
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

        return response

    def read_messages(self):
        """
        Клиент читает входящие сообщения в бесконечном цикле
        """
        while True:
            message = self.receive()  # получаем ответ от сервера
            client_logger.info(f"Принято сообщение: {message}")
            if RESPONSE in message and DATA in message:
                if message[RESPONSE] in range(400, 600) and MESSAGE in message[DATA]:
                    print(f"Ошибка {message[RESPONSE]} - {message[DATA][MESSAGE]}")
                elif message[RESPONSE] in range(100, 400) and MESSAGE in message[DATA]:
                    print(message[DATA][MESSAGE])  # там должно быть сообщение

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
