from server.utils.config_jim import MESSAGE, OK, CONFLICT, ACCEPTED
from server.auth.models import User
from server.contact.models import Contact
from server.utils.decorators import logged
from server.utils.protocol import create_error_response, create_alert_response
from server.utils.server_db import Session


@logged
def get_contact_controller(request):
    request_list = request[MESSAGE].split()
    try:
        user_name = request_list[0]
        contact_name = request_list[1]
    except IndexError:
        print("Не заданы имя пользователя или контакта")
        response = create_error_response(CONFLICT, "Не заданы имя пользователя или контакта")
    else:
        session = Session()
        user = session.query(User).filter_by(name=user_name).first()
        print(f"user = {user}")
        contact = session.query(User).filter_by(name=contact_name).first()
        print(f"contact = {contact}")
        if user and contact:
            contact_exist = session.query(Contact).filter_by(user_id=user.id).filter_by(
                name=contact.name).first()
            if contact_exist:
                response = create_alert_response(ACCEPTED, f"Name: {contact_exist.name} info:{contact_exist.info}")
            else:
                response = create_alert_response(ACCEPTED, "Такого контакта не существует в контакт листе")
        else:
            response = create_alert_response(ACCEPTED, "Такого пользователя или контакта не существует")
        session.commit()
        session.close()
    return response


@logged
def get_contacts_controller(request):
    contact_list = []
    if request[MESSAGE]:
        user_name = request[MESSAGE]
        session = Session()
        user = session.query(User).filter_by(name=user_name).first()
        if user:
            user_id = user.id
            contacts = session.query(Contact).filter_by(user_id=user_id)
            for contact in contacts:
                contact_list.append(contact.name)
            if contact_list:
                response = create_alert_response(ACCEPTED, str(contact_list))
            else:
                response = create_alert_response(ACCEPTED, "Контакт лист пуст")
        else:
            response = create_error_response(CONFLICT, f"Клиент {user_name} не зарегистрирован")
    else:
        print("Не задано имя пользователя")
        response = create_error_response(CONFLICT, "Не задано имя пользователя")
    return response


@logged
def add_contact_controller(request):
    request_list = request[MESSAGE].split()
    try:
        user_name = request_list[0]
        contact_name = request_list[1]
        if len(request_list) > 2:
            info = " ".join(request_list[2:])
        else:
            info = ""
    except IndexError:
        print("Не заданы имя пользователя или контакта")
        response = create_error_response(CONFLICT, "Не заданы имя пользователя или контакта")
    else:
        session = Session()
        user = session.query(User).filter_by(name=user_name).first()
        contact = session.query(User).filter_by(name=contact_name).first()
        if user and contact:
            contact_exist = session.query(Contact).filter_by(user_id=user.id).filter_by(
                name=contact.name).first()
            if contact_exist:
                # response = create_alert_response(OK, contact_exist.name)
                print(f"Contact '{contact_name}' already exists at {user_name}'s contact list")
                response = create_alert_response(
                    ACCEPTED,
                    # f"Contact '{contact_name}' already exists at {user_name}'s contact list"
                    "Contact already exists"
                )
            else:
                new_contact = Contact(name=contact.name, user_id=user.id, info=info)
                session.add(new_contact)
                session.commit()
                print(f"Contact '{contact_name}' added to {user_name}'s contact list")
                response = create_alert_response(
                    ACCEPTED,
                    # f"Contact '{contact_name}' added to {user_name}'s contact list"
                    "Contact added"
                )
        session.commit()
        session.close()
    return response


@logged
def remove_contact_controller(request):
    request_list = request[MESSAGE].split()
    try:
        user_name = request_list[0]
        contact_name = request_list[1]
    except IndexError:
        print("Не заданы имя пользователя или контакта")
        response = create_error_response(CONFLICT, "Не заданы имя пользователя или контакта")
    else:
        session = Session()
        user = session.query(User).filter_by(name=user_name).first()
        print(f"user = {user}")
        contact = session.query(User).filter_by(name=contact_name).first()
        print(f"contact = {contact}")
        if user and contact:
            contact_exist = session.query(Contact).filter_by(user_id=user.id).filter_by(
                name=contact.name).first()
            if contact_exist:
                session.delete(contact_exist)
                session.commit()
                print(f"Contact '{contact_name}' removed from {user_name}'s contact list")
                response = create_alert_response(
                    ACCEPTED,
                    # f"Contact '{contact_name}' removed from {user_name}'s contact list"
                    "Contact removed"
                )
            else:
                print(f"Contact '{contact_name}' does not exist at {user_name}'s contact list")
                response = create_alert_response(
                    ACCEPTED,
                    # f"Contact '{contact_name}' does not exist at {user_name}'s contact list"
                    "Contact does not exist"
                )
        else:
            response = create_alert_response(OK, "Такого пользователя или контакта не существует")
        session.close()
    return response


@logged
def update_contact_controller(request):
    print("Добавление контакта")
    request_list = request[MESSAGE].split()
    try:
        user_name = request_list[0]
        contact_name = request_list[1]
        if len(request_list) > 2:
            info = " ".join(request_list[2:])
        else:
            info = ""
    except IndexError:
        print("Не заданы имя пользователя или контакта")
        response = create_error_response(CONFLICT, "Не заданы имя пользователя или контакта")
    else:
        session = Session()
        user = session.query(User).filter_by(name=user_name).first()
        contact = session.query(User).filter_by(name=contact_name).first()
        if user and contact:
            contact_exist = session.query(Contact).filter_by(user_id=user.id).filter_by(
                name=contact.name).first()
            if contact_exist:
                contact_exist.info = info
                session.commit()
                response = create_alert_response(
                    ACCEPTED,
                    # f"Contact '{contact_name}' updated at {user_name}'s contact list"
                    "Contact updated"
                )
            else:
                print(f"Contact '{contact_name}' does not exist at {user_name}'s contact list")
                response = create_alert_response(
                    ACCEPTED,
                    # f"Contact '{contact_name}' does not exist at {user_name}'s contact list"
                    "Contact does not exist"
                )

        session.close()
    return response
