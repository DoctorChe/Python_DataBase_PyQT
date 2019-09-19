import logging.handlers

from contextlib import suppress
from pathlib import Path

from server.utils.config_server import PROGRAM

LOG_FOLDER_PATH = Path.home() / f".{PROGRAM}" / "logs"

with suppress(FileExistsError):
    LOG_FOLDER_PATH.mkdir(mode=0o777, parents=True, exist_ok=True)

# Путь до серверного лога
SERVER_LOG_FILE_PATH = LOG_FOLDER_PATH / "server.log"

# Создаём именованный объект-логгер с именем server
server_logger = logging.getLogger("server")

# Создаём обработчик с ротацией файлов по дням
server_handler = logging.handlers.TimedRotatingFileHandler(SERVER_LOG_FILE_PATH, when="d", encoding="utf-8")

# Создаём объект форматирования
formatter = logging.Formatter("%(asctime)-10s %(levelname)s %(module)s %(message)s")

# Cвязываем обработчик с форматтером
server_handler.setFormatter(formatter)

server_handler_stream = logging.StreamHandler()
server_handler_stream.setFormatter(formatter)

# Связываем логгер с обработчиком
if not server_logger.__dict__["handlers"]:
    server_logger.addHandler(server_handler)
    server_logger.addHandler(server_handler_stream)

# Устанавливаем уровень сообщений логгера
# server_logger.setLevel(logging.INFO)
server_logger.setLevel(logging.DEBUG)


# отладка
if __name__ == '__main__':
    server_logger.critical('Test critical event')
    server_logger.error('Test error event')
    server_logger.debug('Test debug event')
    server_logger.info('Test info event')
