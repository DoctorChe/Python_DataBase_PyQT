import dis


# Метакласс для проверки корректности клиентов:
class ClientVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        # Список методов, которые используются в функциях класса:
        methods = []
        for func in clsdict:
            # Пробуем
            try:
                ret = dis.get_instructions(clsdict[func])
                # Если не функция то ловим исключение
            except TypeError:
                pass
            else:
                # Раз функция разбираем код, получая используемые методы.
                for i in ret:
                    if i.opname == "LOAD_GLOBAL":
                        if i.argval not in methods:
                            methods.append(i.argval)
        # Если обнаружено использование недопустимого метода accept, listen, socket бросаем исключение:
        for command in ("accept", "listen", "socket"):
            if command in methods:
                raise TypeError(f"В классе обнаружено использование запрещённого метода {command}.")
        # Вызов receive_message или send_message из common_utils считаем корректным использованием сокетов
        if "receive_message" in methods and "send_message" in methods:
            pass
        else:
            raise TypeError("Отсутствуют вызовы функций, работающих с сокетами.")
        super().__init__(clsname, bases, clsdict)
