from jim.config_jim import RESPONSE_CODES, RESPONSE, ERROR, ALERT, ACTION, TIME, MSG, MESSAGE, FROM, TO, DATA

import logging
# from server.utils import server_log_config
from server.utils import server_log_config
from server.utils.decorators import Log

logger = logging.getLogger("server")
log = Log(logger)


def common_check_message(msg: dict) -> bool:
    """
    Базовая проверка сообщения
    :param msg: словарь сообщения
    :return: результат проверки
    """

    def check_length(msg: dict) -> bool:
        if len(str(msg)) <= 640:
            return True
        return False

    def check_action(msg: dict) -> bool:
        if ACTION in msg and len(msg[ACTION]) <= 15:
            return True
        return False

    def check_time(msg: dict) -> bool:
        if TIME in msg and isinstance(msg[TIME], float):
            return True
        return False

    if check_length(msg) and check_action(msg) and check_time(msg):
        return True
    return False


@log
def create_response(request: dict, response_code: int, data=None) -> dict:
    return {
        ACTION: request[ACTION],
        TIME: request[TIME],
        RESPONSE: response_code,
        DATA: data
    }


@log
def create_error_response(response: int, error=None) -> dict:
    """
    Формирование ответа клиенту
    :param response: код ответа
    :param error: текст ошибки
    :return: словарь ответа
    """

    if isinstance(error, str):
        if response in RESPONSE_CODES:
            return {
                RESPONSE: response,
                ERROR: error
            }
    else:
        return {
            RESPONSE: response
        }


@log
def create_alert_response(response: int, alert=None) -> dict:
    """
    Формирование ответа клиенту
    :param response: код ответа
    :param alert: текст сообщения
    :return: словарь ответа
    """

    if isinstance(alert, str):
        if response in RESPONSE_CODES:
            return {
                RESPONSE: response,
                ALERT: alert
            }
    else:
        return {
            RESPONSE: response
        }
