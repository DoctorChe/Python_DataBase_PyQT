# Служебный скрипт запуска/останова нескольких клиентских приложений

import time
from subprocess import Popen, CREATE_NEW_CONSOLE

CLIENTS_COUNT = 2  # Количество клиентов
p_list = []  # Список запущенных процессов

while True:
    action = input(
        f"Запустить сервер и {CLIENTS_COUNT} клиентов (s) / "
        f"Выйти (q) / "
        # f"Закрыть все окна (x) "
    )

    if action == "s":

        # Запускаем сервер
        # Запускаем серверный скрипт и добавляем его в список процессов
        p_list.append(Popen("python server.py",
                            creationflags=CREATE_NEW_CONSOLE))
        print("Сервер запущен")
        time.sleep(1)  # ждем на всякий пожарный

        # Запускаем клиентов
        for i in range(CLIENTS_COUNT):
            # Флаг CREATE_NEW_CONSOLE нужен для ОС Windows,
            # чтобы каждый процесс запускался в отдельном окне консоли
            # p_list.append(Popen(f"python -i client.py -n Console{i}",
            p_list.append(Popen(f"python client.py -n Console{i}",
                                creationflags=CREATE_NEW_CONSOLE))
        print(f" Запущено {CLIENTS_COUNT} клиентов")

    elif action == "q":
        print(f"Открыто процессов {len(p_list)}")
        for p in p_list:
            print(f"Закрываю {p}")
            p.kill()
        p_list.clear()
        print("Выхожу")
        break

    # elif action == 'x':
    #     while p_list:
    #         p_list.pop().kill()
