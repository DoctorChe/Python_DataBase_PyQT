import os
import sys

ENCODING = "utf-8"  # кодировка
MSG_SIZE = 1024  # размер сообщения
WORKERS = 5

DEFAULT_SERVER_IP = ""
DEFAULT_PORT = 7777

# База данных для хранения данных сервера:
SERVER_DATABASE = "sqlite:///server/db/server_db.sqlite3"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROGRAM = "server messenger"
VERSION = "0.7"

INSTALLED_MODULES = (
    # 'auth',
    'echo',
    # 'messenger',
    # 'serverdate',
    # 'servererrors',
)
