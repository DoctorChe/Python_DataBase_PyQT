import hmac
from datetime import datetime

from .decorators import login_required
from .settings import SECRET_KEY
from .utils import authenticate, login
from .models import User, Session
from server.utils.config_jim import OK, DATA, MESSAGE, WRONG_REQUEST, TIME, PASSWORD, LOGIN, TOKEN, CONFLICT
from server.utils.decorators import logged
from server.utils.protocol import create_response
from server.utils.server_db import session_scope


# @logged
def login_controller(request):
    errors = {}
    is_valid = True
    data = request.get(DATA)
    if TIME not in request:
        errors.update({TIME: "Attribute is required"})
        is_valid = False
    if PASSWORD not in data:
        errors.update({PASSWORD: "Attribute is required"})
        is_valid = False
    if LOGIN not in data:
        errors.update({LOGIN: "Attribute is required"})
        is_valid = False

    if not is_valid:
        # return create_response(request, WRONG_REQUEST, {"errors": errors})
        return create_response(request, WRONG_REQUEST, {MESSAGE: errors})

    user = authenticate(data.get(LOGIN), data.get(PASSWORD))

    if user:
        token = login(request, user)
        return create_response(request, OK, {TOKEN: token})

    return create_response(request, WRONG_REQUEST, "Enter correct login or password")


# @logged
def registration_controller(request):
    errors = {}
    is_valid = True
    data = request.get(DATA)

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
    with session_scope() as session:
        user_already_exists = session.query(User).filter_by(name=data.get(LOGIN))
        if user_already_exists.count():
            return create_response(request,
                                   CONFLICT,
                                   {MESSAGE: f"User with login '{data.get(LOGIN)}' already exists"})
        user = User(name=data.get(LOGIN), password=password_digest)
        session.add(user)
    token = login(request, user)
    return create_response(request, OK, {TOKEN: token})


@login_required
def logout_controller(request):
    with session_scope() as session:
        user_session = session.query(Session).filter_by(token=request.get(TOKEN)).first()
        user_session.closed = datetime.now()
        return create_response(request, OK, {MESSAGE: "Session closed"})
