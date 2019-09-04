from server.utils.config_jim import MESSAGE, OK, CONFLICT, ACCEPTED, DATA, ERROR, ALERT
from server.auth.models import User
from server.contact.models import Contact
from server.utils.decorators import logged
from server.utils.protocol import create_response
from server.utils.server_db import session_scope


@logged
def get_contact_controller(request):
    request_list = request[DATA][MESSAGE].split()
    try:
        user_name = request_list[0]
        contact_name = request_list[1]
    except IndexError:
        print("Не заданы имя пользователя или контакта")
        response = create_response(request, CONFLICT, {ERROR: "Не заданы имя пользователя или контакта"})
    else:
        with session_scope() as session:
            user = session.query(User).filter_by(name=user_name).first()
            print(f"user = {user}")
            contact = session.query(User).filter_by(name=contact_name).first()
            print(f"contact = {contact}")
            if user and contact:
                contact_exist = session.query(Contact).filter_by(user_id=user.id).filter_by(
                    name=contact.name).first()
                if contact_exist:
                    response = create_response(
                        request,
                        ACCEPTED,
                        {ALERT: f"Name: {contact_exist.name} info:{contact_exist.info}"}
                    )
                else:
                    response = create_response(
                        request,
                        ACCEPTED,
                        {ALERT: "Такого контакта не существует в контакт листе"}
                    )
            else:
                response = create_response(
                    request,
                    ACCEPTED,
                    {ALERT: "Такого пользователя или контакта не существует"}
                )
    return response


@logged
def get_contacts_controller(request):
    contact_list = []
    if request[DATA][MESSAGE]:
        user_name = request[DATA][MESSAGE]
        with session_scope() as session:
            user = session.query(User).filter_by(name=user_name).first()
            if user:
                user_id = user.id
                contacts = session.query(Contact).filter_by(user_id=user_id)
                for contact in contacts:
                    contact_list.append(contact.name)
                if contact_list:
                    response = create_response(request, ACCEPTED, {ALERT: str(contact_list)})
                else:
                    response = create_response(request, ACCEPTED, {ALERT: "Контакт лист пуст"})
            else:
                response = create_response(request, CONFLICT, {ERROR: f"Клиент {user_name} не зарегистрирован"})
    else:
        print("Не задано имя пользователя")
        response = create_response(request, CONFLICT, {ERROR: "Не задано имя пользователя"})
    return response


@logged
def add_contact_controller(request):
    request_list = request[DATA][MESSAGE].split()
    try:
        user_name = request_list[0]
        contact_name = request_list[1]
        if len(request_list) > 2:
            info = " ".join(request_list[2:])
        else:
            info = ""
    except IndexError:
        print("Не заданы имя пользователя или контакта")
        response = create_response(request, CONFLICT, {ERROR: "Не заданы имя пользователя или контакта"})
    else:
        with session_scope() as session:
            user = session.query(User).filter_by(name=user_name).first()
            contact = session.query(User).filter_by(name=contact_name).first()
            if user and contact:
                contact_exist = session.query(Contact).filter_by(user_id=user.id).filter_by(
                    name=contact.name).first()
                if contact_exist:
                    print(f"Contact '{contact_name}' already exists at {user_name}'s contact list")
                    response = create_response(
                        request,
                        ACCEPTED,
                        {ALERT: "Contact already exists"}
                    )
                else:
                    new_contact = Contact(name=contact.name, user_id=user.id, info=info)
                    session.add(new_contact)
                    print(f"Contact '{contact_name}' added to {user_name}'s contact list")
                    response = create_response(
                        request,
                        ACCEPTED,
                        # f"Contact '{contact_name}' added to {user_name}'s contact list"
                        {ALERT: "Contact added"}
                    )
    return response


@logged
def remove_contact_controller(request):
    request_list = request[DATA][MESSAGE].split()
    try:
        user_name = request_list[0]
        contact_name = request_list[1]
    except IndexError:
        print("Не заданы имя пользователя или контакта")
        response = create_response(request, CONFLICT, {ERROR: "Не заданы имя пользователя или контакта"})
    else:
        with session_scope() as session:
            user = session.query(User).filter_by(name=user_name).first()
            print(f"user = {user}")
            contact = session.query(User).filter_by(name=contact_name).first()
            print(f"contact = {contact}")
            if user and contact:
                contact_exist = session.query(Contact).filter_by(user_id=user.id).filter_by(
                    name=contact.name).first()
                if contact_exist:
                    session.delete(contact_exist)
                    print(f"Contact '{contact_name}' removed from {user_name}'s contact list")
                    response = create_response(
                        request,
                        ACCEPTED,
                        # f"Contact '{contact_name}' removed from {user_name}'s contact list"
                        {ALERT: "Contact removed"}
                    )
                else:
                    print(f"Contact '{contact_name}' does not exist at {user_name}'s contact list")
                    response = create_response(
                        request,
                        ACCEPTED,
                        # f"Contact '{contact_name}' does not exist at {user_name}'s contact list"
                        {ALERT: "Contact does not exist"}
                    )
            else:
                response = create_response(request, OK, {ALERT: "Такого пользователя или контакта не существует"})
    return response


@logged
def update_contact_controller(request):
    print("Добавление контакта")
    request_list = request[DATA][MESSAGE].split()
    try:
        user_name = request_list[0]
        contact_name = request_list[1]
        if len(request_list) > 2:
            info = " ".join(request_list[2:])
        else:
            info = ""
    except IndexError:
        print("Не заданы имя пользователя или контакта")
        response = create_response(request, CONFLICT, {ERROR: "Не заданы имя пользователя или контакта"})
    else:
        with session_scope() as session:
            user = session.query(User).filter_by(name=user_name).first()
            contact = session.query(User).filter_by(name=contact_name).first()
            if user and contact:
                contact_exist = session.query(Contact).filter_by(user_id=user.id).filter_by(
                    name=contact.name).first()
                if contact_exist:
                    contact_exist.info = info
                    response = create_response(
                        request,
                        ACCEPTED,
                        # f"Contact '{contact_name}' updated at {user_name}'s contact list"
                        {ALERT: "Contact updated"}
                    )
                else:
                    print(f"Contact '{contact_name}' does not exist at {user_name}'s contact list")
                    response = create_response(
                        request,
                        ACCEPTED,
                        # f"Contact '{contact_name}' does not exist at {user_name}'s contact list"
                        {ALERT: "Contact does not exist"}
                    )
    return response
