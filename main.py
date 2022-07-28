import json
from os import getenv

from stepn.client import Client


def login(my_client: Client, anonymous_mode: bool = True) -> bool:
    # for the sake of security anonymous mode is turned on by default

    if not anonymous_mode:
        # try to log in using session ID from environment
        session_id = getenv("sessionID")
        my_client.session_id = session_id
        if my_client.ping():
            return True

        # falling back to saved in environment email and password
        email = getenv("email") or input("User E-Mail:")
        password = getenv("password") or input("User password:")
    else:
        email = input("User E-Mail:")
        password = input("User password:")

    # didn't log in with prev credentials
    # reset the session ID
    my_client.session_id = None

    def auth_callback():
        # google authenticator callback
        # called if account is secured with it
        return input("Google authenticator:")

    if my_client.login(email, password, auth_callback):
        if not anonymous_mode:
            # save parameters into JSON file
            # they can later be imported with EnvFile plugin
            with open("env.json", 'w') as environ_file:
                json.dump({
                    "email": email,
                    "password": password,
                    "sessionID": my_client.session_id
                }, environ_file)
        return True
    return False


if __name__ == '__main__':
    client = Client()
    login(client, False)
