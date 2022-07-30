from typing import Optional

from stepn.client import Client, LoginMode
from stepn.util import Environment
from stepn.util.callbacks import prompt


def login(anonymous_mode: bool = True,
          mode: LoginMode = LoginMode.PASSWORD,
          env: Environment = Environment()) -> Optional[Client]:
    """ Attempts to log in into account and, in case of success, returns Client """
    if anonymous_mode:
        # login manually
        client = Client()
        email = input("Enter user E-Mail:")
        password = input("Enter user password:")
        if client.login(email, password, prompt("Enter Google authenticator code:"), mode):
            return client

    else:
        # login
        env_session = env.get_property("sessionID")
        client = Client(env_session)

        if client.ping():
            return client
        else:
            # login using existing E-Mail and password
            email = env.get_property("email", prompt("Enter user E-Mail:"))
            password = env.get_property("password", prompt("Enter user password:"))

            if client.login(email, password, prompt("Enter Google authenticator code:"), mode):
                # noinspection PyUnboundLocalVariable
                # since 'env' is only used in 'public' mode
                env.set_property("email", email)
                env.set_property("password", password)
                env.set_property("sessionID", client.session_id)
                env.save()
                return client
    # return None
