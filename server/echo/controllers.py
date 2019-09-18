from datetime import datetime
from functools import reduce

from .models import Message

from server.utils.decorators import logged
from server.utils.server_db import session_scope
from server.utils.config_jim import OK, WRONG_REQUEST, DATA, MESSAGE
from server.utils.protocol import create_response


@logged
def echo_controller(request):
    data = request[DATA]
    with session_scope() as session:
        # message = Message(data=data[MESSAGE])
        message = Message(data=data[MESSAGE], created=datetime.now())
        session.add(message)
    return create_response(request, OK, data)


@logged
def delete_message_controller(request):
    # message_id = request.get("message_id")
    message_id = request[DATA][MESSAGE]
    with session_scope() as session:
        message = session.query(Message).filter_by(id=message_id).first()
        session.delete(message)
    return create_response(request, OK)


@logged
def update_message_controller(request):
    # message_id = request.get("message_id")
    # message_data = request.get("message_data")

    request_list = request[DATA][MESSAGE].split()
    try:
        message_id = request_list[0]
        message_data = " ".join(request_list[1:])
    except IndexError:
        # print("Не задан id или текст сообщения")
        return create_response(request, WRONG_REQUEST, {MESSAGE: "Не задан id или текст сообщения"})
    else:
        with session_scope() as session:
            message = session.query(Message).filter_by(id=message_id).first()
            message.data = message_data
        return create_response(request, OK)


@logged
def get_messages_controller(request):
    with session_scope() as session:
        messages = reduce(
            lambda value, item: value + [
                {MESSAGE: item.data, "created": item.created.timestamp()}
            ],
            session.query(Message).all(),
            []
        )
        return create_response(request, OK, {MESSAGE: str(messages)})
