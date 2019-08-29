from jim.config_jim import ACTION, ECHO
from .controllers import (
    echo_controller,
    get_messages_controller,
    update_message_controller,
    delete_message_controller
)

action_names = [
    {ACTION: ECHO, "controller": echo_controller},
    {ACTION: "get_all_messages", "controller": get_messages_controller},
    {ACTION: "update_message", "controller": update_message_controller},
    {ACTION: "delete_message", "controller": delete_message_controller},
]
