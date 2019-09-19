from server.utils.config_jim import ACTION, PRESENCE, ACT_LOGIN, ACT_LOGOUT, ACT_REGISTRATION
from .controllers import (
    # user_login_controller,
    login_controller,
    registration_controller,
    logout_controller,
)

action_names = [
    # {ACTION: PRESENCE, "controller": user_login_controller},
    {ACTION: ACT_LOGIN, "controller": login_controller},
    {ACTION: ACT_LOGOUT, "controller": logout_controller},
    {ACTION: ACT_REGISTRATION, "controller": registration_controller},
]
