import logging
import os

# Папка где лежит настоящий файл
LOG_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
# Путь до клиентского лога
CLIENT_LOG_FILE_PATH = os.path.join(LOG_FOLDER_PATH, "client.log")

# Создаём именованный объект-логгер с именем server
client_logger = logging.getLogger("client")

# Устанавливаем уровень сообщений логгера
client_logger.setLevel(logging.INFO)

# Создаём обработчик
client_handler = logging.FileHandler(CLIENT_LOG_FILE_PATH, encoding="utf-8")

# Устанавливаем уровень сообщений обработчика
client_logger.setLevel(logging.INFO)

# Создаём объект форматирования
formatter = logging.Formatter("%(asctime)-10s %(levelname)s %(module)s %(message)s")

# Связываем обработчик с форматтером
client_handler.setFormatter(formatter)

# Связываем логгер с обработчиком
client_logger.addHandler(client_handler)
