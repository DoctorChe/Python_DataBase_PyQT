import os

from server_app import Server
from utils.parser import create_parser
from utils.handlers import handle_process_client_message
from utils.server_db import Base
from utils.config_server import INSTALLED_MODULES, BASE_DIR


parser = create_parser()

if parser.parse_args().migrate:
    print(BASE_DIR)
    # module_name_list = [f"{item}.models" for item in INSTALLED_MODULES]
    module_name_list = [f"server.{item}.models" for item in INSTALLED_MODULES]
    print(f'module_name_list = {module_name_list}')
    module_path_list = (os.path.join(BASE_DIR, item, "models.py") for item in INSTALLED_MODULES)
    # print(f'module_path_list = {list(module_path_list)}')
    # for path in ['C:\\Program1\\PythonProjects\\Python_DataBase_PyQT\\server\\auth\\models.py', 'C:\\Program1\\PythonProjects\\Python_DataBase_PyQT\\server\\contact\\models.py', 'C:\\Program1\\PythonProjects\\Python_DataBase_PyQT\\server\\echo\\models.py']:
    #     print(f'path = {path}')
    for index, path in enumerate(module_path_list):
        # print(f'path = {path}')
        if os.path.exists(path):
            __import__(module_name_list[index])
            # print(f'module {module_name_list[index]} was imported')
    Base.metadata.create_all()

else:
    with Server(
            (parser.parse_args().addr, parser.parse_args().port),
            handle_process_client_message
    ) as server:
        server.run()
        # server.daemon = True
        # server.start()
