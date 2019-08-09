from errors import UsernameToLongError

import logging
logger = logging.getLogger('client')


# Дескриптор для описания имени клиента:
class ClientName:
    def __set__(self, instance, value):
        # value - имя клиента
        # Если имя прошло проверку, добавляем его в список атрибутов экземпляра
        if not isinstance(value, str):
            # Заполняем лог
            res = "Попытка запуска клиента с именем не являющимся строкой."
            logger.error(f"{res} - {value}")
            raise TypeError
        if len(value) > 25:
            # Заполняем лог
            res = "Попытка запуска клиента со слишком длинным именем."
            logger.error(f"{res} - {value} - {len(value)} символов")
            raise UsernameToLongError(value)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        # owner - <class '__main__.Client'>
        # name - __name
        self.name = name
