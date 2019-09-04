from server.utils.config_jim import MESSAGE, OK, WRONG_REQUEST, TIME, PASSWORD, LOGIN, DATA, ALERT
from server.auth.models import User
from server.utils.decorators import logged
from server.utils.protocol import create_response
from server.utils.server_db import session_scope


@logged
def user_login_controller(request):
    name = request[DATA][MESSAGE]
    with session_scope() as session:
        result = session.query(User).filter_by(name=name)

        # Если имя пользователя уже присутствует в таблице, обновляем время последнего входа
        if result.count():
            user = result.first()
            # user.last_login = datetime.datetime.now()
        # Если нету, то создаздаём нового пользователя
        else:
            user = User(name=name)
            session.add(user)
    response = create_response(request, OK, {ALERT: ""})
    # else:
    #     # TODO: отработать ситуацию, если имя пользователя уже занято
    return response
