import json
import threading

from client.utils.config_client import MSG_SIZE
from client.utils.protocol import create_message
from client.utils.config_jim import RESPONSE, RESPONSE_CODES, MESSAGE, DATA
from client.utils.message import (compress_middleware, encrypt_middleware, to_json_middleware, from_json_middleware,
                                  decrypt_middleware, decompress_middleware)
from client.utils.metaclasses import ClientVerifier
from client.utils.errors import (ResponseCodeError, ResponseCodeLenError, MessageIsNotDictError, MandatoryKeyError)
from client.utils.descriptors import CheckedHost, ClientName

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

    @to_json_middleware
    @encrypt_middleware
    @compress_middleware
    def send(self, request):
        self._socket.send(request)

    @from_json_middleware
    @decrypt_middleware
    @decompress_middleware
    def receive(self):
        return self._socket.recv(MSG_SIZE)

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
        action = input("Enter action: ")
        dict_data = json.loads(input("Enter data: "))

        # json_string = "{" + f'"{MESSAGE}": "{data}"' + "}"
        # {"text": "test"}

        # registration
        # {"login": "Duncan", "password": "pass"}

        message = create_message(action, dict_data)
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
        r_thread = threading.Thread(target=self.read_messages)
        r_thread.daemon = True
        r_thread.start()
        while True:
            self.write_messages()
