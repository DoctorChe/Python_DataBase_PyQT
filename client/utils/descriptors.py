import ipaddress
import socket
from .errors import UsernameToLongError

from client.utils.config_log_client import client_logger


class ClientName:
    """Дескриптор для проверки имени клиента"""
    # def __get__(self, instance, owner):
    #     # owner - класс
    #     return instance.__dict__[self.name]

    def __set__(self, instance, value):
        # value - имя клиента
        # Если имя прошло проверку, добавляем его в список атрибутов экземпляра
        if not isinstance(value, str):
            # Заполняем лог
            res = "Попытка запуска клиента с именем не являющимся строкой."
            client_logger.error(f"{res} - {value}")
            raise TypeError
        if len(value) > 25:
            # Заполняем лог
            res = "Попытка запуска клиента со слишком длинным именем."
            client_logger.error(f"{res} - {value} - {len(value)} символов")
            raise UsernameToLongError(value)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        # owner - <class '__main__.Client'>
        # name - _name
        self.name = name


class CheckedHost:
    """Дескриптор для проверки сокета"""
    def __set__(self, instance, value):
        # value - host = (ip, port)
        ip, port = value

        # Проверяем адрес
        if not check_ip(hostname_to_ip(ip)):
            client_logger.critical(
                f"Попытка запуска клиента с неподходящим ip-адресом: {ip}. Клиент завершается.")
            raise ValueError(
                f"Попытка запуска клиента с неподходящим ip-адресом: {ip}. Клиент завершается.")

        # Проверяем порт
        if not isinstance(port, int):
            # Заполняем лог
            res = f"Попытка запуска клиента с портом не являющимся целым числом: {port}."
            client_logger.error(f"{res} - {port}")
            raise TypeError(f"Попытка запуска клиента с портом не являющимся целым числом: {port}.")
        if not 1023 < port < 65536:
            client_logger.critical(
                f"Попытка запуска клиента с неподходящим номером порта: {port}. "
                f"Допустимы адреса с 1024 до 65535. Клиент завершается.")
            raise ValueError(
                f"Попытка запуска клиента с неподходящим номером порта: {port}. "
                f"Допустимы адреса с 1024 до 65535. Клиент завершается.")
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        # owner - <class '__main__.Client'>
        # name - _name
        self.name = name


def hostname_to_ip(name):
    try:
        host = socket.gethostbyname(name)
    except socket.gaierror as err:
        print(f'Не удается разрешить имя хоста: {name} {err}')
        return None
    else:
        return host


def check_ip(ip):
    try:
        ip = str(ipaddress.ip_address(ip))
    except ipaddress.AddressValueError as err:
        print(f"Недопусмый ip-адрес: {ip} {err}")
        return None
    else:
        return ip
