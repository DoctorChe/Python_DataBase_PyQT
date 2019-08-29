import time

from jim.config_jim import ACTION, MSG, TIME, TO, FROM, MESSAGE, QUIT, ACCOUNT_NAME, GET_CONTACTS, GET_CONTACT, \
    ADD_CONTACT, DEL_CONTACT, UPDATE_CONTACT, INFO


# Функция создаёт текстовое сообщение
# def create_message(action, message_to, message_from, text):
def create_echo_message(action, text):
    return {
        # ACTION: MSG,
        ACTION: action,
        TIME: time.time(),
        # TO: message_to,
        # FROM: message_from,
        MESSAGE: text
    }


# Функция создаёт текстовое сообщение
# def create_message(action, message_to, message_from, text):
def create_message(action, text):
    return {
        # ACTION: MSG,
        ACTION: action,
        TIME: time.time(),
        # TO: message_to,
        # FROM: message_from,
        MESSAGE: text
    }


# Функция создаёт словарь с сообщением о выходе
def create_exit_message(name):
    return {
        ACTION: QUIT,
        TIME: time.time(),
        ACCOUNT_NAME: name
    }


# Функция создаёт словарь с сообщением о получении списка контактов
def get_contact_list(name):
    return {
        ACTION: GET_CONTACTS,
        TIME: time.time(),
        ACCOUNT_NAME: name
    }


# Функция создаёт словарь с сообщением о получении информации о контакте
def get_contact(name, contact_name):
    return {
        ACTION: GET_CONTACT,
        TIME: time.time(),
        ACCOUNT_NAME: name,
        TO: contact_name
    }


# Функция создаёт словарь с сообщением для добавления контакта в список контактов
def add_contact(name, contact_name):
    return {
        ACTION: ADD_CONTACT,
        TIME: time.time(),
        ACCOUNT_NAME: name,
        TO: contact_name
    }


# Функция создаёт словарь с сообщением для удаления контакта из списка контактов
def remove_contact(name, contact_name):
    return {
        ACTION: DEL_CONTACT,
        TIME: time.time(),
        ACCOUNT_NAME: name,
        TO: contact_name
    }


# Функция создаёт словарь с сообщением для обновления информации о контакте
def update_contact(name, contact_name, info):
    return {
        ACTION: UPDATE_CONTACT,
        TIME: time.time(),
        ACCOUNT_NAME: name,
        TO: contact_name,
        INFO: info
    }
