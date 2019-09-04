import time

from utils.config_jim import ACTION, TIME, MESSAGE, DATA


# Функция создаёт текстовое сообщение
def create_message(action, text):
    return {
        ACTION: action,
        TIME: time.time(),
        # TO: message_to,
        # FROM: message_from,
        DATA: {MESSAGE: text}
    }
