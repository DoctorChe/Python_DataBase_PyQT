from jim.config_jim import ACTION, PRESENCE
from .controllers import (
    user_login_controller,
)

action_names = [
    {ACTION: PRESENCE, "controller": user_login_controller},
]
