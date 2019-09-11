from utils.config_jim import ACTION, ECHO, ACT_GET_ALL_MESSAGES, ACT_UPDATE_MESSAGE, ACT_DELETE_MESSAGE
from .controllers import (
    echo_controller,
    get_messages_controller,
    update_message_controller,
    delete_message_controller
)

action_names = [
    {ACTION: ECHO, "controller": echo_controller},
    {ACTION: ACT_GET_ALL_MESSAGES, "controller": get_messages_controller},
    {ACTION: ACT_UPDATE_MESSAGE, "controller": update_message_controller},
    {ACTION: ACT_DELETE_MESSAGE, "controller": delete_message_controller},
]
