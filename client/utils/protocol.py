import time

from jim.config_jim import ACTION, TIME, MESSAGE


# Функция создаёт текстовое сообщение
def create_message(action, text):
    return {
        ACTION: action,
        TIME: time.time(),
        # TO: message_to,
        # FROM: message_from,
        MESSAGE: text
    }
