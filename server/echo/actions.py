from .controllers import (
    echo_controller,
    get_messages_controller,
    update_message_controller,
    delete_message_controller
)

actionnames = [
    {"action": "echo", "controller": echo_controller},
    {"action": "get_all_messages", "controller": get_messages_controller},
    {"action": "update_message", "controller": update_message_controller},
    {"action": "delete_message", "controller": delete_message_controller},
]
