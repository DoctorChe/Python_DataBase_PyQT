import ipaddress
import socket

import logging
from server.utils import server_log_config
# from server.utils import server_log_config
from server.utils.decorators import Log

logger = logging.getLogger("server")
log = Log(logger)


class CheckedHost:
    """Дескриптор для проверки сокета"""
    def __set__(self, instance, value):
        # value - host = (ip, port)
        ip, port = value

        # Проверяем адрес
        if not check_ip(hostname_to_ip(ip)):
            logger.critical(
                f"Попытка запуска клиента с неподходящим ip-адресом: {ip}. Клиент завершается.")
            raise ValueError(
                f"Попытка запуска клиента с неподходящим ip-адресом: {ip}. Клиент завершается.")

        # Проверяем порт
        if not isinstance(port, int):
            # Заполняем лог
            res = f"Попытка запуска клиента с портом не являющимся целым числом: {port}."
            logger.error(f"{res} - {port}")
            raise TypeError(f"Попытка запуска клиента с портом не являющимся целым числом: {port}.")
        if not 1023 < port < 65536:
            logger.critical(
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
        print(f"Не удается разрешить имя хоста: {name} {err}")
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
