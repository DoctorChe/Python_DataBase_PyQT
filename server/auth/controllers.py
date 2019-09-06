import hmac
from datetime import datetime

from auth.decorators import login_required
from auth.settings import SECRET_KEY
from auth.utils import authenticate, login
from server.utils.config_jim import OK, DATA, MESSAGE, WRONG_REQUEST, TIME, PASSWORD, LOGIN, TOKEN
from server.auth.models import User, Session
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
    # response = create_response(request, OK, {MESSAGE: ""})
    response = create_response(request, OK)
    # else:
    #     # TODO: отработать ситуацию, если имя пользователя уже занято
    return response


# @logged
def login_controller(request):
    errors = {}
    is_valid = True
    data = request[DATA]

    if TIME not in request:
        errors.update({TIME: "Attribute is required"})
        is_valid = False
    if PASSWORD not in data:
        errors.update({PASSWORD: "Attribute is required"})
        is_valid = False
    if LOGIN not in data:
        errors.update({LOGIN: 'Attribute is required'})
        is_valid = False

    if not is_valid:
        # return create_response(request, WRONG_REQUEST, {"errors": errors})
        return create_response(request, WRONG_REQUEST, {MESSAGE: errors})

    # user = authenticate(data.get('login'), data.get('password'))
    user = authenticate(data[LOGIN], data[PASSWORD])

    if user:
        token = login(request, user)
        return create_response(request, OK, {TOKEN: token})

    return create_response(request, WRONG_REQUEST, "Enter correct login or password")


# @logged
def registration_controller(request):
    print("registration_controller started")
    errors = {}
    is_valid = True
    data = request[DATA]

    if PASSWORD not in data:
        errors.update({PASSWORD: "Attribute is required"})
        is_valid = False
    if LOGIN not in data:
        errors.update({LOGIN: "Attribute is required"})
        is_valid = False

    if not is_valid:
        # return create_response(request, WRONG_REQUEST, {"errors": errors})
        return create_response(request, WRONG_REQUEST, {MESSAGE: errors})

    hmac_obj = hmac.new(SECRET_KEY.encode(), data.get(PASSWORD).encode())
    password_digest = hmac_obj.hexdigest()

    with session_scope() as db_session:
        user = User(name=data.get(LOGIN), password=password_digest)
        db_session.add(user)
    token = login(request, user)
    return create_response(request, OK, {TOKEN: token})


@login_required
def logout_controller(request):
    with session_scope() as db_session:
        user_session = db_session.query(Session).filter_by(token=request.get(TOKEN)).first()
        user_session.closed = datetime.now()
        return create_response(request, OK, "Session closed")
