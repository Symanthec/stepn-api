from typing import *

from requests import get, JSONDecodeError

from .loginmode import LoginMode
from .passhash import PasswordHasher


class Client:
    __url_prefix = "https://api.stepn.com/run/"

    STATUS_CODE = 'code'
    RESPONSE_DATA = 'data'
    ERROR_MESSAGE = 'msg'

    @property
    def session_id(self):
        return self.__session_id

    @session_id.setter
    def session_id(self, value):
        self.__session_id = value

    def __init__(self, new_session_id=None):
        self.session_id = new_session_id

    def extract_data(self, dictionary: dict) -> Any:
        return dictionary[self.RESPONSE_DATA] or None

    def is_response_good(self, response: dict) -> bool:
        return response[self.STATUS_CODE] == 0

    def ping(self) -> bool:
        """ Requests basic user info. If response contains code 0, then sessionID is valid. """
        try:
            return self.userbasic()[self.STATUS_CODE] == 0
        except RuntimeError:
            return False

    def login(self, email: str, password: Union[int, str], auth_callback: Callable[[], str],
              mode: LoginMode = LoginMode.PASSWORD) -> bool:
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
        response = self.run("login", **url_params)
        if self.is_response_good(response):
            data = self.extract_data(response)
            self.session_id = data["sessionID"]

            login = True
            if data['gAuthState'] == 1:
                # requires google authentication
                login = self.do_code_check(auth_callback())

            if login:
                return True

        # reset session ID
        self.session_id = None
        return False

    def run(self, command: str, __method=get, **parameters) -> dict:
        parameters["sessionID"] = self.session_id
        response = __method(self.__url_prefix + command, params=parameters)

        try:
            body = response.json()
        except JSONDecodeError:
            body = None

        if body is None:
            url = response.request.url.split("?")[0]
            raise RuntimeError(f"Error occurred while accessing {url}\n{response.text}")
        return body

    def do_code_check(self, code: Union[int, str]) -> bool:
        return self.is_response_good(self.run('doCodeCheck', codeData=f"2:{code}"))

    def userbasic(self):
        return self.run("userbasic")

    def order_data(self, order_id: Union[int, str]):
        return self.extract_data(self.run("orderdata", orderId=order_id)) or {}

    def order_list(self, **order_query) -> []:
        return self.extract_data(self.run("orderlist", **order_query)) or []

    def buy_prop(self, order_id: Union[int, str], price: Union[int, str]) -> bool:
        return self.is_response_good(self.run("buyprop", orderID=order_id, price=price))
