import argparse
from utils.config_main import DEFAULT_SERVER_IP, DEFAULT_CLIENT_IP, DEFAULT_PORT, PROGRAM, VERSION


def create_parser(server=False):
    """
    Создание объекта парсера командной строки
    :param server: тип создаваемого объекта (сервер или клиент)
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
    if server:
        ip = DEFAULT_SERVER_IP
    else:
        ip = DEFAULT_CLIENT_IP
    # parser.add_argument("-m", "--mode",
    #                     default="r",
    #                     type=str,
    #                     choices={"r", "w"},
    #                     help="Режим работы клиента (r - чтение, w - запись)")
    parser.add_argument("-n", "--name",
                        default="Guest",
                        type=str,
                        help="Имя клиента")
    parser.add_argument("-a", "--addr",
                        default=ip,
                        type=str,
                        help="IP адрес")
    parser.add_argument("-p", "--port",
                        default=DEFAULT_PORT,
                        type=int,
                        help="Номер порта")
    return parser
