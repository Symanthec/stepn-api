from stepn.util import Environment
from stepn.client import Client


def login(my_client: Client, anonymous_mode: bool = True) -> bool:
    if not anonymous_mode:
        env = Environment()
        my_client.session_id = env.get_property("sessionID")
        if my_client.ping():
            return True

        email = env.get_property("email") or input("Enter user E-Mail:")
        password = env.get_property("password") or input("Enter user password:")
    else:
        my_client = Client()

        email = input("User E-Mail:")
        password = input("User password:")

    def auth_callback():
        # Google authenticator callback
        # Only called if account is secured with it
        return input("Enter Google authenticator code:")

    if my_client.login(email, password, auth_callback):
        if not anonymous_mode:
            # noinspection PyUnboundLocalVariable
            # since 'env' is only used in 'public' mode
            env.set_property("email", email)
            env.set_property("password", password)
            env.set_property("sessionID", my_client.session_id)
            env.save()
        return True
    return False


if __name__ == '__main__':
    client = Client()
    if login(client, False):
        print("Logged in!")
