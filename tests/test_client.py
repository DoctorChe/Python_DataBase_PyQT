import os
import sys
import time
import unittest

sys.path.append(os.path.join(os.getcwd(), ".."))

from client.client_app import Client
from jim.config import ACTION, TIME, USER, ACCOUNT_NAME, STATUS
from client.utils.config_main import DEFAULT_CLIENT_IP, DEFAULT_PORT
from client.errors import UsernameToLongError, MandatoryKeyError, ResponseCodeLenError, ResponseCodeError


# тестируем создание экземпляра класса
class TestClientInstance(unittest.TestCase):

    # тестируем создание экземпляра класса Client без передачи обязательного параметра host
    def test_instant_creation_no_host(self):
        with self.assertRaises(TypeError):
            client = Client()
            client.close()

    # неверный тип аккаунта - число
    def test_instant_creation_acc_int(self):
        with self.assertRaises(TypeError):
            client = Client((DEFAULT_CLIENT_IP, DEFAULT_PORT), 123)
            print(f"client.name = {client.name} ({type(client.name)})")
            client.close()

    # # верный тип аккаунта
    # def test_instant_creation_acc_int(self):
    #     with self.assertRaises(TypeError):
    #         client = Client((DEFAULT_CLIENT_IP, DEFAULT_PORT), "OK")
    #         client.close()

    # неверный тип аккаунта - None
    def test_instant_creation_acc_none(self):
        with self.assertRaises(TypeError):
            client = Client((DEFAULT_CLIENT_IP, DEFAULT_PORT), None)
            client.close()

    # слишком длинное имя аккаунта ( длиннее 25 символов)
    def test_instant_creation_acc_toolong(self):
        with self.assertRaises(UsernameToLongError):
            client = Client((DEFAULT_CLIENT_IP, DEFAULT_PORT), "A"*26)
            client.close()

    # проверяем, что имя клиента записывается корректно, если мы его передаем
    def test_instant_creation_guest(self):
        client = Client((DEFAULT_CLIENT_IP, DEFAULT_PORT))
        # account_name = client.get_name()
        account_name = client.name
        self.assertEqual(account_name, "Guest")
        client.close()

    # проверяем, что имя клиента записывается корректно, если мы его передаем
    def test_instant_creation_param(self):
        client = Client((DEFAULT_CLIENT_IP, DEFAULT_PORT), "test_user_name")
        # account_name = client.get_name()
        account_name = client.name
        self.assertEqual(account_name, "test_user_name")
        client.close()


# тестируем функцию создания соединения клиентом
class TestClientConnect(unittest.TestCase):

    # тестируем создание соединения без сервера
    def test_connect_no_server(self):
        client = Client((DEFAULT_CLIENT_IP, DEFAULT_PORT))
        connection = client.connect()
        self.assertEqual(connection, False)
        client.close()


# тестируем функцию формирования сообщения от клиента
class TestClientCreatePresence(unittest.TestCase):
    # action формируется корректно
    def test_create_presence_non(self):
        client = Client((DEFAULT_CLIENT_IP, DEFAULT_PORT))
        presence = client.create_presence()
        self.assertEqual(presence[ACTION], "presence")
        client.close()

    # берем разницу во времени
    def test_create_presence_time(self):
        client = Client((DEFAULT_CLIENT_IP, DEFAULT_PORT))
        presence = client.create_presence()
        self.assertTrue(abs(presence[TIME] - time.time()) < 0.1)
        client.close()

    # проверяем, что имя клиента записывается корректно, если мы его передаем
    def test_create_presence_guest(self):
        client = Client((DEFAULT_CLIENT_IP, DEFAULT_PORT))
        presence = client.create_presence()
        self.assertEqual(presence[USER][ACCOUNT_NAME], "Guest")
        client.close()

    # проверяем, что имя клиента записывается корректно, если мы его передаем
    def test_create_presence_param(self):
        client = Client((DEFAULT_CLIENT_IP, DEFAULT_PORT), "test_user_name")
        presence = client.create_presence()
        self.assertEqual(presence[USER][ACCOUNT_NAME], "test_user_name")
        client.close()

    # проверяем, что статус клиента записывается корректно, если мы его передаем
    def test_create_presence_status(self):
        client = Client((DEFAULT_CLIENT_IP, DEFAULT_PORT), "test_user_name")
        presence = client.create_presence("test_status")
        self.assertEqual(presence[USER][STATUS], "test_status")
        client.close()

    # проверяем, что имя аккаунта записалось правильное (тип str)
    def test_create_presence_acc_int(self):
        client = Client((DEFAULT_CLIENT_IP, DEFAULT_PORT))
        presence = client.create_presence()
        self.assertEqual(type(presence[USER][ACCOUNT_NAME]), str)
        client.close()

    # проверяем, что имя аккаунта записалось правильное (длина не более 25 символов)
    def test_create_presence_acc_none(self):
        client = Client((DEFAULT_CLIENT_IP, DEFAULT_PORT))
        presence = client.create_presence()
        self.assertEqual(len(presence[USER][ACCOUNT_NAME]) <= 25, True)
        client.close()

    # тестируем функцию разбора ответа сервера
    class TestClientTranslateMessage(unittest.TestCase):
        # неправильный тип
        def test_translate_message_inc_type(self):
            with self.assertRaises(TypeError):
                client = Client((DEFAULT_CLIENT_IP, DEFAULT_PORT))
                client.translate_message(100)
                client.close()

        # нету ключа response
        def test_translate_message_not_resp(self):
            with self.assertRaises(MandatoryKeyError):
                client = Client((DEFAULT_CLIENT_IP, DEFAULT_PORT))
                client.translate_message({"one": "two"})
                client.close()

        # неверная длина кода ответа
        def test_translate_message_incor_resp_len(self):
            with self.assertRaises(ResponseCodeLenError):
                client = Client((DEFAULT_CLIENT_IP, DEFAULT_PORT))
                client.translate_message({"response": "5"})
                client.close()

        # неверный код ответа
        def test_translate_message_incor_resp(self):
            with self.assertRaises(ResponseCodeError):
                client = Client((DEFAULT_CLIENT_IP, DEFAULT_PORT))
                client.translate_message({"response": "700"})
                client.close()

        # все правильно
        def test_translate_message_cor_resp(self):
            client = Client((DEFAULT_CLIENT_IP, DEFAULT_PORT))
            self.assertEqual(client.translate_message({'response': 200}), {'response': 200})
            client.close()


if __name__ == "__main__":
    unittest.main()
