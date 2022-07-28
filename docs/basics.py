from stepn.client import Client, LoginMode


def login(email, password) -> Client:
    # Client class automates requests to STEPN API
    client = Client()

    # To use it, you must log in

    # To log in, you need to know your account's E-Mail
    # email = "mail@example.org"

    # Password can be either your password, or verification code
    # password = "123456"

    """ 
    Despite the possibility, Client won't implement the ability to 
    ask STEPN to send verification codes, as it would be exploited by
    abusers or mail spam bots
    """

    # Since account can be protected with Google Authenticator
    # You should define a callback, which will return the code
    def auth_callback() -> str:
        return input("Enter Google authenticator code:")

    # As with application, you can enter either via password...
    mode = LoginMode.PASSWORD
    # ... or verification code
    # mode = LoginMode.AUTHCODE

    """
    You don't have to specify mode. Then client will try to login by password.
    """

    # Now we may log in
    success = client.login(email, password, auth_callback, mode)
    if success:
        print("I've learned basics of stepn-api library!")
        return client


if __name__ == '__main__':
    new_client = login()

    # After successful login, you can claim session ID
    session_id = new_client.session_id

    # You can't log in with one account on two clients
    # However, you can then feed your session_id into another client
    second_client = Client(session_id)

    # Also you can check, if the session ID that you provided is working by calling
    if second_client.ping():
        print("Now two clients can work simultaneously!")
