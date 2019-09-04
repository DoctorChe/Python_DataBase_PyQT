from socket import socket, AF_INET, SOCK_STREAM

from client.client_app import Client
from utils.parser import create_parser
from utils.protocol import create_message
from utils.config_jim import PRESENCE, RESPONSE, OK, GET_CONTACTS, ACCEPTED, ALERT

from client.utils.config_log_client import client_logger

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
        response = client.receive()  # получаем ответ от сервера
        response = client.translate_message(response)  # разбираем сообщение от сервера
        if response[RESPONSE] == OK:
            client_logger.info("Соединение с сервером установлено")
            message = create_message(GET_CONTACTS, account_name)  # запрашиваем список контактов
            client.send(message)  # отправляем сообщение серверу
            response = client.receive()  # получаем ответ от сервера
            response = client.translate_message(response)  # разбираем сообщение от сервера
            if response[RESPONSE] == ACCEPTED:
                if ALERT in response:
                    client_logger.info(f"Плучен список контактов: {response[ALERT]}")
                else:
                    client_logger.info("Список контактов пуст")
            # print("Формат сообщения:\n"
            #       "message <получатель> <текст>")
            client.run()
