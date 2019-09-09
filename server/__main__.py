import os

from server_app import Server
from utils.parser import create_parser
from utils.handlers import handle_process_client_message
from utils.server_db import Base
from utils.config_server import INSTALLED_MODULES, BASE_DIR


parser = create_parser()

if parser.parse_args().migrate:
    module_name_list = [f"server.{item}.models" for item in INSTALLED_MODULES]
    module_path_list = (os.path.join(BASE_DIR, item, "models.py") for item in INSTALLED_MODULES)
    for index, path in enumerate(module_path_list):
        if os.path.exists(path):
            __import__(module_name_list[index])
    Base.metadata.create_all()

else:
    with Server(
            (parser.parse_args().addr, parser.parse_args().port),
            handle_process_client_message
    ) as server:
        server.run()
        # server.daemon = True
        # server.start()
