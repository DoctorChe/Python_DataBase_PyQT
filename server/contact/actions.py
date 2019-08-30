from jim.config_jim import ACTION, GET_CONTACT, GET_CONTACTS, ADD_CONTACT, DEL_CONTACT, UPDATE_CONTACT
from .controllers import (
    get_contact_controller,
    get_contacts_controller,
    add_contact_controller,
    remove_contact_controller,
    update_contact_controller,
)

action_names = [
    {ACTION: GET_CONTACTS, "controller": get_contacts_controller},
    {ACTION: GET_CONTACT, "controller": get_contact_controller},
    {ACTION: ADD_CONTACT, "controller": add_contact_controller},
    {ACTION: DEL_CONTACT, "controller": remove_contact_controller},
    {ACTION: UPDATE_CONTACT, "controller": update_contact_controller},
]
