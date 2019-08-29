from jim.config_jim import ACTION, WRONG_REQUEST, SERVER_ERROR, NOT_FOUND
from server.utils.protocol import common_check_message, create_error_response
from server.utils.resolvers import resolve

import logging
# from server.utils import server_log_config
from server.utils import server_log_config
from server.utils.decorators import Log

logger = logging.getLogger("server")
log = Log(logger)


# Обработчик сообщений от клиентов, принимает словарь - сообщение от клиента, проверяет корректность, формирует ответ
def handle_process_client_message(message: dict):
    logger.debug(f"Разбор сообщения от клиента : {message}")
    # Если это сообщение о присутствии, принимаем и отвечаем
    if common_check_message(message):
        action_name = message.get(ACTION)
        print(f"action_name = {action_name}")
        controller = resolve(action_name)
        print(f"controller = {controller}")
        if controller:
            try:
                logger.debug(f"Controller {action_name} resolved with request: {message}")
                response = controller(message)
            except Exception as err:
                logging.critical(f"Controller {action_name} error: {err}")
                # response = create_response(message, SERVER_ERROR, "Internal server error")
                response = create_error_response(SERVER_ERROR, "Internal server error")
        else:
            logging.error(f'Controller {action_name} not found')
            # response = create_response(message, NOT_FOUND, f"Action with name {action_name} not supported")
            response = create_error_response(NOT_FOUND, f"Action with name {action_name} not supported")
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
        # if (
        #         message[ACTION] == MSG and
        #         TO in message and
        #         FROM in message and
        #         MESSAGE in message
        # ):
        #     # print(f"Обрабатывается пересылка сообщения: {message}")
        #     response = create_response(message, OK, message[MESSAGE])
        #     # print(f"Сформирован код ответа {OK} и ответ: {response} на сообщение {message}")
        #     # if message[TO] in self.names.keys():
        #     #     # TODO: отработать ситуацию попытки отправки сообщения самому себе
        #     #     if message[TO] == message[FROM]:
        #     #         response = create_error_response(NOT_FOUND, "Попытка отправки сообщения самому себе")
        #     #         print(f"Попытка отправки сообщения самому себе ('{message[TO]}')")
        #     #         send_message(client, response)
        #     #     else:
        #     #         self.messages.append(message)
        #     # # TODO: отработать ситуацию когда получатель сообщения не найден
        #     # else:
        #     #     response = create_error_response(NOT_FOUND, "Получатель сообщения не найден")
        #     #     print(f"Не найден клиент с именем '{message[TO]}'")
        #     #     send_message(client, response)
        #     # return
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
        # # Если клиент запрашивает список контактов
        # elif (
        #         message[ACTION] == GET_CONTACTS and
        #         ACCOUNT_NAME in message
        # ):
        #     print(f"Запрос списка контактов от клиента '{message[ACCOUNT_NAME]}'")
        #     contact_list = database.get_contacts(message[ACCOUNT_NAME])
        #     response = create_alert_response(ACCEPTED, str(contact_list))
        # # Если клиент запрашивает информацию о контакте из списка контактов
        # elif (
        #         message[ACTION] == GET_CONTACT and
        #         ACCOUNT_NAME in message and
        #         TO in message
        # ):
        #     print(f"Запрос информации о контакте '{message[TO]}' "
        #           f"из списка контактов от клиента '{message[ACCOUNT_NAME]}'")
        #     contact = database.get_contact(message[ACCOUNT_NAME], message[TO])
        #     response = create_alert_response(ACCEPTED, contact.information)
        # # Если клиент пытается добавить контакт в список контактов
        # elif (
        #         message[ACTION] == ADD_CONTACT and
        #         ACCOUNT_NAME in message and
        #         TO in message
        # ):
        #     print(f"Запрос на добавление контакта '{message[TO]}' "
        #           f"в список контактов от клиента '{message[ACCOUNT_NAME]}'")
        #     database.add_contact(message[ACCOUNT_NAME], message[TO])
        #     response = create_alert_response(ACCEPTED, "Contact added")
        # # Если клиент пытается удалить контакт из списка контактов
        # elif (
        #         message[ACTION] == DEL_CONTACT and
        #         ACCOUNT_NAME in message and
        #         TO in message
        # ):
        #     print(f"Запрос на удаление контакта '{message[TO]}' "
        #           f"из списка контактов от клиента '{message[ACCOUNT_NAME]}'")
        #     database.remove_contact(message[ACCOUNT_NAME], message[TO])
        #     response = create_alert_response(ACCEPTED, "Contact removed")
        # # Если клиент пытается обновить контакт в списке контактов
        # elif (
        #         message[ACTION] == UPDATE_CONTACT and
        #         ACCOUNT_NAME in message and
        #         TO in message and
        #         INFO in message
        # ):
        #     print(f"Запрос на удаление контакта '{message[TO]}' "
        #           f"из списка контактов от клиента '{message[ACCOUNT_NAME]}'")
        #     database.update_contact(message[ACCOUNT_NAME], message[TO], message[INFO])
        #     response = create_alert_response(ACCEPTED, "Contact updated")
    # Иначе отдаём Bad request
    else:
        logging.error(f"Запрос некорректен: {message}")
        # response = create_response(message, WRONG_REQUEST, "Запрос некорректен.")
        response = create_error_response(WRONG_REQUEST, "Запрос некорректен.")
    return response
