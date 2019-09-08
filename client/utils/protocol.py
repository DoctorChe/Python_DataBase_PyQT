import hashlib
from datetime import datetime

from utils.config_jim import ACTION, TIME, MESSAGE, DATA, TOKEN


# # Функция создаёт текстовое сообщение
# def create_message(action, data):
#     hash_obj = hashlib.sha256()
#     hash_obj.update(str(datetime.now().timestamp()).encode())
#     return {
#         ACTION: action,
#         TIME: datetime.now().timestamp(),
#         # DATA: {MESSAGE: text},
#         DATA: data,
#         TOKEN: hash_obj.hexdigest(),
#     }


def make_request(action, data, token):
    return {
        'action': action,
        'time': datetime.now().timestamp(),
        'data': data,
        'token': token
    }
