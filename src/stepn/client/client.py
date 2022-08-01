import logging
from typing import Union, Callable, Dict, List, Optional

from requests import JSONDecodeError, Session

from .loginmode import LoginMode
from .passhash import PasswordHasher
from .response import Response


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
        self.session = Session()
        self.session_id = new_session_id

    def ping(self) -> bool:
        """ Requests basic user info. If response contains code 0, then sessionID is valid. """
        return self.userbasic() is not None

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

        if response := self.run("login", **url_params):
            data = response.get_data()
            self.session_id = data["sessionID"]
            if data['gAuthState'] == 1:
                # requires google authentication
                return self.do_code_check(auth_callback())
            else:
                return True
        # reset session ID
        self.session_id = None
        return False

    def run(self, command: str, **parameters) -> Optional[Response]:
        parameters["sessionID"] = self.session_id
        url = self.__url_prefix + command
        web_response = self.session.get(url, params=parameters)

        try:
            response = Response(web_response.json())
        except JSONDecodeError:
            logging.error(f"Error occurred while accessing {url}:\n{web_response.text}")
            return None

        return response

    def do_code_check(self, code: Union[int, str]) -> bool:
        return self.run('doCodeCheck', codeData=f"2:{code}").is_successful()

    def userbasic(self) -> Response:
        return self.run("userbasic")

    def order_data(self, order_id: Union[int, str]) -> Dict:
        return self.run("orderdata", orderId=order_id).get_data() or {}

    def order_list(self, **order_query) -> List:
        return self.run("orderlist", **order_query).get_data() or []

    def buy_prop(self, order_id: Union[int, str], price: Union[int, str]) -> bool:
        return self.run("buyprop", orderID=order_id, price=price).is_successful()
