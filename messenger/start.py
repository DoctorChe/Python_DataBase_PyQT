# Служебный скрипт запуска/останова нескольких клиентских приложений

import time
from subprocess import Popen, CREATE_NEW_CONSOLE

READ_CLIENTS_COUNT = 3  # Читающие клиенты
WRITE_CLIENTS_COUNT = 2  # Пишущие клиенты
p_list = []  # Список запущенных процессов

while True:
    user = input(f"Запустить сервер и "
                 f"{READ_CLIENTS_COUNT} клиентов на запись и "
                 f"{WRITE_CLIENTS_COUNT} клиентов на чтение (s) / "
                 f"Выйти (q) ")

    if user == "s":
        # Запускаем сервер
        # Запускаем серверный скрипт и добавляем его в список процессов
        p_list.append(Popen("python server.py",
                            creationflags=CREATE_NEW_CONSOLE))
        print("Сервер запущен")
        time.sleep(1)  # ждем на всякий пожарный
        for _ in range(READ_CLIENTS_COUNT):
            # Флаг CREATE_NEW_CONSOLE нужен для ОС Windows,
            # чтобы каждый процесс запускался в отдельном окне консоли
            p_list.append(Popen("python -i client.py -m r",
                                creationflags=CREATE_NEW_CONSOLE))
        print(f" Запущено {READ_CLIENTS_COUNT} клиентов на чтение")
        for _ in range(WRITE_CLIENTS_COUNT):
            p_list.append(Popen("python -i client.py -m w",
                                creationflags=CREATE_NEW_CONSOLE))
        print(f" Запущено {WRITE_CLIENTS_COUNT} клиентов на запись")
    elif user == "q":
        print(f"Открыто процессов {len(p_list)}")
        for p in p_list:
            print(f"Закрываю {p}")
            p.kill()
        p_list.clear()
        print("Выхожу")
        break
