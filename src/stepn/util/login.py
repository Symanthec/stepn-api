import logging
from typing import Optional

from ..client import Client, LoginMode
from ..util import Environment
from ..util.callbacks import prompt, google_auth_dialog


def login(anonymous_mode: bool = True,
          mode: LoginMode = LoginMode.PASSWORD,
          env: Environment = Environment(),
          attempts: int = 2) -> Optional[Client]:
    """ Attempts to log in into account and, in case of success, returns Client """
    if anonymous_mode:
        # login manually
        client = Client(google_auth_dialog())
        email = input("Enter user E-Mail:")
        password = input("Enter user password:")

        for attempt in range(attempts):
            if attempt > 0:
                logging.warning(f"Login reattempt #{attempt}")
            if client.login(email, password, mode):
                return client

    else:
        # login
        env_session = env.get_property("sessionID")
        client = Client(google_auth_dialog(env), env_session)

        if env_session and client.ping():
            return client
        else:
            # login using existing E-Mail and password
            email = env.get_property_or_run("email", prompt("Enter user E-Mail:"))
            password = env.get_property_or_run("password", prompt("Enter user password:"))

            for attempt in range(attempts):
                if attempt > 0:
                    logging.warning(f"Login reattempt #{attempt}")
                if client.login(email, password, mode):
                    # noinspection PyUnboundLocalVariable
                    # since 'env' is only used in 'public' mode
                    env.set_property("email", email)
                    env.set_property("password", password)
                    env.set_property("sessionID", client.session_id)
                    env.save()
                    return client
    # return None
