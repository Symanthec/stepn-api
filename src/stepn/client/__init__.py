from .passhash import PasswordHasher
from .loginmode import LoginMode

from typing import *
from requests import get, Response


class Client:
    __url_prefix = "https://api.stepn.com/run/"

    @property
    def session_id(self):
        return self.__session_id

    @session_id.setter
    def session_id(self, value):
        self.__session_id = value

    def __init__(self, new_session_id=None):
        self.session_id = new_session_id

    def ping(self) -> bool:
        """ Requests basic user info. If response contains code 0, then sessionID is valid. """
        try:
            return self.run("userbasic")['code'] == 0
        except RuntimeError:
            return False

    def login(self, email: str, password: str, auth_callback: Callable[[], str], mode: LoginMode = LoginMode.PASSWORD) \
            -> bool:
        """
        Attempts to generate Session ID by trying to log in as a StepN user
        :param auth_callback: function to be called, that should return Google authenticator code
        :param email: user E-Mail
        :param password: user password or authentication code, sent to e-mail
        :param mode: determines, whether "password" field is password or e-mail code
        :return: true, if logged in successfully
        """
        url_params = {
            "account": email,
            "password": PasswordHasher.hash_password(email, password, mode),
            "type": mode.value,
            "deviceInfo": "web"
        }
        response = self.run("login", url_params)
        if response["code"] == 0:
            data = response['data']
            self.session_id = data["sessionID"]

            login = True
            if data['gAuthState'] == 1:
                # requires google authentication
                url_params = {
                    "codeData": f"2:{auth_callback()}",
                    "sessionID": self.session_id
                }
                response = self.run('doCodeCheck', url_params)
                login = response['code'] == 0

            if login:
                return True

        # reset session ID
        self.session_id = None
        return False

    def run(self, command: str, parameters=None, method=get) -> Response:
        if parameters is None:
            parameters = {}
        parameters["sessionID"] = self.session_id
        response = method(self.__url_prefix + command, params=parameters)
        return response.json()
