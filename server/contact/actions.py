from .controllers import (
    get_contact_controller,
    get_contacts_controller,
    add_contact_controller,
    remove_contact_controller,
    update_contact_controller,
)

action_names = [
    {"action": "get_contact", "controller": get_contact_controller},
    {"action": "get_contacts", "controller": get_contacts_controller},
    {"action": "add_contact", "controller": add_contact_controller},
    {"action": "remove_contact", "controller": remove_contact_controller},
    {"action": "update_contact", "controller": update_contact_controller},
]
