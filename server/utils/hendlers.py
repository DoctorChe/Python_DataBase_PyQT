import json

from utils.config_jim import ACTION, WRONG_REQUEST, SERVER_ERROR, NOT_FOUND, ERROR
from utils.config_server import ENCODING
from utils.middlewares import compression_middleware, encryption_middleware
from utils.protocol import common_check_message, create_response
from utils.resolvers import resolve
from utils.config_log_server import server_logger


@compression_middleware
@encryption_middleware
def handle_process_client_message(raw_message):
    message = json.loads(raw_message.decode(ENCODING))

    server_logger.debug(f"Разбор сообщения от клиента : {message}")
    if common_check_message(message):
        action_name = message[ACTION]
        controller = resolve(action_name)
        if controller:
            try:
                server_logger.debug(f"Controller {action_name} resolved with request: {message}")
                response = controller(message)
            except Exception as err:
                server_logger.critical(f"Controller {action_name} error: {err}")
                response = create_response(message, SERVER_ERROR, {ERROR: "Internal server error"})
        else:
            server_logger.error(f'Controller {action_name} not found')
            response = create_response(message, NOT_FOUND, {ERROR: f"Action with name {action_name} not supported"})
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
        #     self._clients.remove(client)
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
        #     #         self._messages.append(message)
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
        #     self._clients.remove(self.names[message[ACCOUNT_NAME]])
        #     self.names[message[ACCOUNT_NAME]].close()
        #     del self.names[message[ACCOUNT_NAME]]
        #     return
    # Иначе отдаём Bad request
    else:
        server_logger.error(f"Запрос некорректен: {message}")
        response = create_response(message, WRONG_REQUEST, {ERROR: "Запрос некорректен."})
    return json.dumps(response).encode(ENCODING)
