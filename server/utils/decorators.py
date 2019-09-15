"""
Модуль, содержащий декораторы.
"""

from functools import wraps

# from server.utils.config_log_server import server_logger
from .config_log_server import server_logger


class Log:
    """
    Класс декоратор для логирования функций
    """

    def __init__(self, logger):
        # запоминаем логгер, чтобы можно было использовать разные
        self.logger = logger

    @staticmethod
    def _create_message(result=None, *args, **kwargs):
        """
        Формирует сообщение для записи в лог
        :param result: результат работы функции
        :param args: любые параметры по порядку
        :param kwargs: любые именованные параметры
        :return: сообщение для записи в лог
        """
        message = ""
        if args:
            message = f"{message}args: {args}"
        if kwargs:
            message = f"{message} kwargs: {kwargs}"
        if result:
            message = f"{message} = {result}"
        # Возвращаем итоговое сообщение
        return message

    def __call__(self, func):
        """
        Определяем __call__ для возможности вызова экземпляра как декоратора
        :param func: функция которую будем декорировать
        :return: новая функция
        """

        @wraps(func)
        def decorated(*args, **kwargs):
            # Выполняем функцию и получаем результат
            result = func(*args, **kwargs)
            # Формируем сообщение в лог
            message = Log._create_message(result, *args, **kwargs)
            # Пишем сообщение в лог
            self.logger.debug(f"{message} - {decorated.__name__} - {decorated.__module__}")
            return result

        return decorated


logged = Log(server_logger)
