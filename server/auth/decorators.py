from functools import wraps

from auth.models import Session
from utils.config_jim import FORBIDDEN, MESSAGE, TOKEN
from utils.protocol import create_response
from utils.server_db import session_scope


def login_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if TOKEN not in request:
            return create_response(request, FORBIDDEN, {MESSAGE: "Access denied"})
        with session_scope() as session:
            user_session = session.query(Session).filter_by(token=request[TOKEN]).first()
            if not user_session or user_session.closed:
                return create_response(request, FORBIDDEN, {MESSAGE: "Access denied"})

        return func(request, *args, **kwargs)
    return wrapper
