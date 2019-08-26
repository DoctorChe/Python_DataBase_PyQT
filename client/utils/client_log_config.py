import logging
import os

from client.utils.config_client import ENCODING

# Родительская папка от папки где лежит настоящий файл + вложенная папка logs
LOG_FOLDER_PATH = os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)),
    "logs"
)

try:
    os.makedirs(LOG_FOLDER_PATH)  # пытаемся создать папку для логов
except FileExistsError:
    # directory already exists
    pass

# Путь до клиентского лога
CLIENT_LOG_FILE_PATH = os.path.join(LOG_FOLDER_PATH, "client.log")

# Создаём именованный объект-логгер с именем server
client_logger = logging.getLogger("client")

# # Устанавливаем уровень сообщений логгера
# client_logger.setLevel(logging.INFO)

# Создаём обработчик
client_handler = logging.FileHandler(CLIENT_LOG_FILE_PATH, encoding=ENCODING)

# Устанавливаем уровень сообщений обработчика
client_logger.setLevel(logging.INFO)

# Создаём объект форматирования
formatter = logging.Formatter("%(asctime)-10s %(levelname)s %(module)s %(message)s")

# Связываем обработчик с форматтером
client_handler.setFormatter(formatter)

# Связываем логгер с обработчиком
client_logger.addHandler(client_handler)


# отладка
if __name__ == '__main__':
    client_logger.critical('Test critical event')
    client_logger.error('Test error event')
    client_logger.debug('Test debug event')
    client_logger.info('Test info event')
