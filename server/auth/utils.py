import hmac
import hashlib
from datetime import datetime

from server.utils.config_jim import TIME
from server.utils.server_db import session_scope

from .settings import SECRET_KEY
from .models import User, Session


def authenticate(login, password):
    with session_scope() as session:
        user = session.query(User).filter_by(name=login).first()
        hmac_obj = hmac.new(SECRET_KEY.encode(), password.encode())
        password_digest = hmac_obj.hexdigest()
        if user and hmac.compare_digest(password_digest.encode(), user.password.encode()):
            return user


def login(request, user):
    with session_scope() as session:
        hash_obj = hashlib.sha256()
        hash_obj.update(SECRET_KEY.encode())
        hash_obj.update(str(request[TIME]).encode())
        token = hash_obj.hexdigest()
        user_session = Session(user=user, token=token, created=datetime.now())
        session.add(user_session)
        return token
