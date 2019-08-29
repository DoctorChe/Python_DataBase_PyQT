from jim.config_jim import ACTION, MSG, TO, FROM, MESSAGE, OK, GET_CONTACTS, ACCOUNT_NAME, ACCEPTED, GET_CONTACT, \
    ADD_CONTACT, DEL_CONTACT, UPDATE_CONTACT, INFO, WRONG_REQUEST
from server.utils.protocol import common_check_message, create_response, create_alert_response, create_error_response

import logging
# from server.utils import server_log_config
from server.utils import server_log_config
from server.utils.decorators import Log

logger = logging.getLogger("server")
log = Log(logger)


# Обработчик сообщений от клиентов, принимает словарь - сообщение от клиента, проверяет корректность, формирует ответ
# def handle_process_client_message(self, message: dict, client: socket):
def handle_process_client_message(message: dict, database):
    logger.debug(f"Разбор сообщения от клиента : {message}")
    # Если это сообщение о присутствии, принимаем и отвечаем
    # print(f"Сообщение: {message} передано на валидацию")
    if common_check_message(message):
        # print(f"Сообщение: {message} прошло валидацию")
        # TODO: сделать регистрацию клиентов
        # if (
        #         message[ACTION] == PRESENCE and
        #         USER in message
        # ):
        # Если такой пользователь ещё не зарегистрирован, регистрируем,
        # иначе отправляем ответ и завершаем соединение.
        # if message[USER][ACCOUNT_NAME] not in self.names.keys():
        #     self.names[message[USER][ACCOUNT_NAME]] = client
        #     client_ip, client_port = client.getpeername()
        #     self.database.user_login(message[USER][ACCOUNT_NAME], client_ip, client_port)
        #     response = create_error_response(OK)
        #     # send_message(client, response)
        # TODO: отработать ситуацию, если имя пользователя уже занято
        # else:
        #     response = create_error_response(CONFLICT, "Имя пользователя уже занято.")
        #     send_message(client, response)
        #     self.clients.remove(client)
        #     client.close()
        # return
        # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
        # elif (
        if (
                message[ACTION] == MSG and
                TO in message and
                FROM in message and
                MESSAGE in message
        ):
            # print(f"Обрабатывается пересылка сообщения: {message}")
            response = create_response(message, OK, message[MESSAGE])
            # print(f"Сформирован код ответа {OK} и ответ: {response} на сообщение {message}")
            # if message[TO] in self.names.keys():
            #     # TODO: отработать ситуацию попытки отправки сообщения самому себе
            #     if message[TO] == message[FROM]:
            #         response = create_error_response(NOT_FOUND, "Попытка отправки сообщения самому себе")
            #         print(f"Попытка отправки сообщения самому себе ('{message[TO]}')")
            #         send_message(client, response)
            #     else:
            #         self.messages.append(message)
            # # TODO: отработать ситуацию когда получатель сообщения не найден
            # else:
            #     response = create_error_response(NOT_FOUND, "Получатель сообщения не найден")
            #     print(f"Не найден клиент с именем '{message[TO]}'")
            #     send_message(client, response)
            # return
        # Если клиент выходит
        # elif (
        #         message[ACTION] == QUIT and
        #         ACCOUNT_NAME in message
        # ):
        #     self.database.user_logout(message[ACCOUNT_NAME])
        #     print(f"Клиент '{message[ACCOUNT_NAME].fileno()} {message[ACCOUNT_NAME].getpeername()}' отключился")
        #     self.clients.remove(self.names[message[ACCOUNT_NAME]])
        #     self.names[message[ACCOUNT_NAME]].close()
        #     del self.names[message[ACCOUNT_NAME]]
        #     return
        # Если клиент запрашивает список контактов
        elif (
                message[ACTION] == GET_CONTACTS and
                ACCOUNT_NAME in message
        ):
            print(f"Запрос списка контактов от клиента '{message[ACCOUNT_NAME]}'")
            contact_list = database.get_contacts(message[ACCOUNT_NAME])
            response = create_alert_response(ACCEPTED, str(contact_list))
            # send_message(client, response)
            # return
        # Если клиент запрашивает информацию о контакте из списка контактов
        elif (
                message[ACTION] == GET_CONTACT and
                ACCOUNT_NAME in message and
                TO in message
        ):
            print(f"Запрос информации о контакте '{message[TO]}' "
                  f"из списка контактов от клиента '{message[ACCOUNT_NAME]}'")
            contact = database.get_contact(message[ACCOUNT_NAME], message[TO])
            response = create_alert_response(ACCEPTED, contact.information)
            # send_message(client, response)
            # return
        # Если клиент пытается добавить контакт в список контактов
        elif (
                message[ACTION] == ADD_CONTACT and
                ACCOUNT_NAME in message and
                TO in message
        ):
            print(f"Запрос на добавление контакта '{message[TO]}' "
                  f"в список контактов от клиента '{message[ACCOUNT_NAME]}'")
            database.add_contact(message[ACCOUNT_NAME], message[TO])
            response = create_alert_response(ACCEPTED, "Contact added")
            # send_message(client, response)
            # return
        # Если клиент пытается удалить контакт из списка контактов
        elif (
                message[ACTION] == DEL_CONTACT and
                ACCOUNT_NAME in message and
                TO in message
        ):
            print(f"Запрос на удаление контакта '{message[TO]}' "
                  f"из списка контактов от клиента '{message[ACCOUNT_NAME]}'")
            database.remove_contact(message[ACCOUNT_NAME], message[TO])
            response = create_alert_response(ACCEPTED, "Contact removed")
            # send_message(client, response)
            # return
        # Если клиент пытается обновить контакт в списке контактов
        elif (
                message[ACTION] == UPDATE_CONTACT and
                ACCOUNT_NAME in message and
                TO in message and
                INFO in message
        ):
            print(f"Запрос на удаление контакта '{message[TO]}' "
                  f"из списка контактов от клиента '{message[ACCOUNT_NAME]}'")
            database.update_contact(message[ACCOUNT_NAME], message[TO], message[INFO])
            response = create_alert_response(ACCEPTED, "Contact updated")
            # send_message(client, response)
            # return
    # Иначе отдаём Bad request
    else:
        response = create_error_response(WRONG_REQUEST, "Запрос некорректен.")
        # send_message(client, response)
        # return
    return response
