import os
import sys
import unittest

from server.utils.protocol import common_check_message

sys.path.append(os.path.join(os.getcwd(), ".."))

from server.utils.config_jim import TIME, ACTION, PRESENCE, STATUS
from server.utils.config_server import DEFAULT_SERVER_IP, DEFAULT_PORT, SERVER_DATABASE
from server.server_app import Server


class TestServerInstance(unittest.TestCase):

    # тестируем создание экземпляра класса Client без передачи обязательного параметра host
    def test_instant_creation_no_host(self):
        with self.assertRaises(TypeError):
            Server()


# class TestServerCreateResponse(unittest.TestCase):
#
#     # нет ключа action
#     def test_action_response(self):
#         msg = {
#             "one": "two",
#             TIME: time.time()
#         }
#         server = Server((DEFAULT_SERVER_IP, DEFAULT_PORT), SERVER_DATABASE)
#         # response = server.create_error_response(msg)
#         response = server.handle_process_client_message(msg)
#         self.assertEqual(response, {RESPONSE: 400, MESSAGE: 'Неправильный запрос/JSON объект'})
#
#     # ключ action имеет значение не presence
#     def test_presence_response(self):
#         msg = {
#             ACTION: "test_action",
#             TIME: 1000.10
#         }
#         server = Server((DEFAULT_SERVER_IP, DEFAULT_PORT), SERVER_DATABASE)
#         response = server.create_error_response(msg)
#         self.assertEqual(response, {RESPONSE: 400, MESSAGE: 'Неправильный запрос/JSON объект'})
#
#     # нет ключа time
#     def test_time_response(self):
#         msg = {
#             ACTION: PRESENCE
#         }
#         server = Server((DEFAULT_SERVER_IP, DEFAULT_PORT), SERVER_DATABASE)
#         response = server.create_error_response(msg)
#         self.assertEqual(response, {RESPONSE: 400, MESSAGE: 'Неправильный запрос/JSON объект'})
#
#     # неправильное время
#     def test_time_incorrect_response(self):
#         msg = {
#             ACTION: PRESENCE,
#             TIME: "test_time"
#         }
#         server = Server((DEFAULT_SERVER_IP, DEFAULT_PORT), SERVER_DATABASE)
#         response = server.create_error_response(msg)
#         self.assertEqual(response, {RESPONSE: 400, MESSAGE: 'Неправильный запрос/JSON объект'})
#
#     # правильное время
#     def test_time_correct_response(self):
#         msg = {
#             ACTION: PRESENCE,
#             TIME: 1000.10,
#         }
#         server = Server((DEFAULT_SERVER_IP, DEFAULT_PORT), SERVER_DATABASE)
#         response = server.create_error_response(msg)
#         self.assertEqual(response, {'response': 200})


# базовая проверка полученного сообщения
class TestServerCheckMessage(unittest.TestCase):

    # слишком длинное сообщение ( > 640 символов)
    def test_long_message(self):
        msg = {
            ACTION: PRESENCE,
            TIME: 1000.10,
            STATUS: "A" * 640,
        }
        server = Server((DEFAULT_SERVER_IP, DEFAULT_PORT), SERVER_DATABASE)
        self.assertEqual(common_check_message(msg), False)

    # слишком длинное сообщение ( > 15 символов)
    def test_long_action(self):
        msg = {
            ACTION: "A" * 16,
            TIME: 1000.10,
        }
        server = Server((DEFAULT_SERVER_IP, DEFAULT_PORT), SERVER_DATABASE)
        self.assertEqual(common_check_message(msg), False)

    # слишком длинное сообщение
    def test_time_incorrect(self):
        msg = {
            ACTION: PRESENCE,
            TIME: "test_time",
        }
        server = Server((DEFAULT_SERVER_IP, DEFAULT_PORT), SERVER_DATABASE)
        self.assertEqual(common_check_message(msg), False)


if __name__ == "__main__":
    unittest.main()
