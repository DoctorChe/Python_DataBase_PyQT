import argparse
from .config_server import DEFAULT_SERVER_IP, DEFAULT_PORT, PROGRAM, VERSION


def create_parser():
    """
    Создание объекта парсера командной строки
    :return: объект ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog=PROGRAM,
        description="""Программа для обмена сообщениями""",
        epilog="""(c) Doctor_Che 2019. Автор программы, как всегда, не несет никакой ответственности ни за что.""",
        add_help=False
    )
    parser.add_argument("-h", "--help",
                        action="help",
                        help="Справка")
    parser.add_argument("-v", "--version",
                        action="version",
                        help="Вывести номер версии",
                        version=f"{PROGRAM} {VERSION}")
    parser.add_argument("-a", "--addr",
                        default=DEFAULT_SERVER_IP,
                        type=str,
                        help="IP адрес")
    parser.add_argument("-p", "--port",
                        default=DEFAULT_PORT,
                        type=int,
                        help="Номер порта")
    parser.add_argument("-m", "--migrate",
                        action="store_true",
                        help="Осуществить миграцию")
    return parser
