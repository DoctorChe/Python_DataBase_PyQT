from utils.config_jim import RESPONSE_CODES, RESPONSE, ACTION, TIME, DATA
from utils.config_log_server import server_logger
from utils.decorators import logged


def common_check_message(msg: dict) -> bool:
    """
    Базовая проверка сообщения
    :param msg: словарь сообщения
    :return: результат проверки
    """

    def check_length(msg: dict) -> bool:
        if len(str(msg)) <= 640:
            return True
        # server_logger.error("Message length more than 640 symbols")
        server_logger.error("Длина сообщения более чем 640 символов")
        return False

    def check_action(msg: dict) -> bool:
        # if ACTION in msg and len(msg[ACTION]) <= 15:
        if ACTION in msg and len(msg[ACTION]) <= 25:
            return True
        server_logger.error(f"Атрибут {ACTION} отсутствует или он длиннее 25 символов")
        return False

    def check_time(msg: dict) -> bool:
        if TIME in msg and isinstance(msg[TIME], float):
            return True
        server_logger.error(f"Атрибут {TIME} отсутствует или имеет неверный тип")
        return False

    if check_length(msg) and check_action(msg) and check_time(msg):
        return True
    return False


@logged
def create_response(request: dict, response_code: int, data=None) -> dict:
    if response_code in RESPONSE_CODES:
        return {
            ACTION: request[ACTION],
            TIME: request[TIME],
            RESPONSE: response_code,
            DATA: data
        }
