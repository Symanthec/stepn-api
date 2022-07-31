from typing import Optional

from stepn.client import Client, LoginMode
from stepn.util import Environment
from stepn.util.callbacks import prompt, google_auth_dialog


def login(anonymous_mode: bool = True,
          mode: LoginMode = LoginMode.PASSWORD,
          env: Environment = Environment(),
          attempts: int = 2) -> Optional[Client]:
    """ Attempts to log in into account and, in case of success, returns Client """
    if anonymous_mode:
        # login manually
        client = Client()
        email = input("Enter user E-Mail:")
        password = input("Enter user password:")
        for it in range(attempts):
            if it > 0:
                print(f"Login attempt #{it}")
            if client.login(email, password, google_auth_dialog(), mode):
                return client

    else:
        # login
        env_session = env.get_property("sessionID")
        client = Client(env_session)

        if env_session and client.ping():
            return client
        else:
            # login using existing E-Mail and password
            email = env.get_property_or_run("email", prompt("Enter user E-Mail:"))
            password = env.get_property_or_run("password", prompt("Enter user password:"))
            auth_callback = google_auth_dialog(env)

            for it in range(attempts):
                if it > 0:
                    print(f"Login attempt #{it}")
                if client.login(email, password, auth_callback, mode):
                    # noinspection PyUnboundLocalVariable
                    # since 'env' is only used in 'public' mode
                    env.set_property("email", email)
                    env.set_property("password", password)
                    env.set_property("sessionID", client.session_id)
                    env.save()
                    return client
    # return None
