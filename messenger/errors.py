"""Все ошибки"""


class MessageIsNotDictError(Exception):
    """
    Исключение: передаваемое сообщение не является словарём
    """
    def __str__(self):
        return "Передаваемое сообщение не является словарём."


class ResponseCodeError(Exception):
    """
    Исключение: переданный код отсутствует среди стандартных кодов
    """
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return f"Неверный код ответа {self.code}."


class ResponseCodeLenError(ResponseCodeError):
    """
    Исключение: длина кода - не три символа
    """
    def __str__(self):
        return f"Неверная длина кода {self.code}. Длина кода должна быть 3 символа."


class MandatoryKeyError(Exception):
    """
    Исключение: отсутствует обязательный атрибут response
    """
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return f"Не хватает обязательного атрибута {self.key}."


class UsernameToLongError(Exception):
    """
    Исключение: имя пользователя слишком длинное - более 25 символов
    """
    def __init__(self, username):
        self.username = username

    def __str__(self):
        return f"Имя пользователя {self.username} должно быть менее 26 символов."
