from functools import reduce

from server.utils.server_db import Session
# from decorators import logged
from server.utils.config_jim import MESSAGE, OK, WRONG_REQUEST
from server.utils.protocol import create_response, create_error_response
from .models import Message


# @logged
def echo_controller(request):
    # data = request.get(MESSAGE)
    data = request[MESSAGE]
    session = Session()
    message = Message(data=data)
    session.add(message)
    session.commit()
    session.close()
    return create_response(request, OK, data)


def delete_message_controller(request):
    # message_id = request.get("message_id")
    # message_id = request.get(MESSAGE)
    message_id = request[MESSAGE]
    session = Session()
    message = session.query(Message).filter_by(id=message_id).first()
    session.delete(message)
    session.commit()
    session.close()
    return create_response(request, OK)


def update_message_controller(request):
    # message_id = request.get("message_id")
    # message_data = request.get("message_data")

    request_list = request[MESSAGE].split()
    try:
        message_id = request_list[0]
        message_data = " ".join(request_list[1:])
    except IndexError:
        # print("Не задан id или текст сообщения")
        return create_error_response(WRONG_REQUEST, "Не задан id или текст сообщения")
    else:
        session = Session()
        message = session.query(Message).filter_by(id=message_id).first()
        message.data = message_data
        session.commit()
        session.close()
        return create_response(request, OK)


# @logged
def get_messages_controller(request):
    session = Session()
    messages = reduce(
        lambda value, item: value + [
            {"data": item.data, "created": item.created.timestamp()}
        ],
        session.query(Message).all(),
        []
    )
    return create_response(request, OK, messages)
