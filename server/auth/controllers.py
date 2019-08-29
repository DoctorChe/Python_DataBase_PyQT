from jim.config_jim import MESSAGE, OK
from server.auth.models import User
from server.utils.protocol import create_alert_response
from server.utils.server_db import Session


def user_login_controller(request):
    name = request[MESSAGE]
    session = Session()
    # user = session.query(User).filter_by(name=name).first()
    result = session.query(User).filter_by(name=name)

    # Если имя пользователя уже присутствует в таблице, обновляем время последнего входа
    if result.count():
        user = result.first()
        # user.last_login = datetime.datetime.now()
    # Если нету, то создаздаём нового пользователя
    else:
        user = User(name=name)
        session.add(user)
        session.commit()
        session.close()
    response = create_alert_response(OK)
    # else:
    #     # TODO: отработать ситуацию, если имя пользователя уже занято
    #     response = create_error_response(CONFLICT, "Имя пользователя уже занято.")
    return response

