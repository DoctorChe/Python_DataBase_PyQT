from server.utils.config_jim import ACTION, PRESENCE, LOGIN, LOGOUT, REGISTRATION
from .controllers import (
    user_login_controller,
    # login_controller,
)

action_names = [
    {ACTION: PRESENCE, "controller": user_login_controller},
    # {ACTION: LOGIN, "controller": login_controller},
    # {ACTION: LOGOUT, "controller": logout_controller},
    # {ACTION: REGISTRATION, "controller": registration_controller},
]
