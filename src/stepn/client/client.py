import logging
from typing import Union, Callable, Dict, List, Optional

from requests import JSONDecodeError, Session

from .loginmode import LoginMode
from .passhash import PasswordHasher
from .response import Response
from ..order import Order
from ..typing import JsonNumber


class Client:
    __url_prefix = "https://apilb.stepn.com/run/"

    def __init__(self, auth_callback: Callable[[], str], new_session_id=None):
        self.get_auth_code = auth_callback
        self.session = Session()
        self.session_id = new_session_id

    def ping(self) -> bool:
        """ Requests basic user info. If response contains code 0, then sessionID is valid. """
        return self.userbasic().is_successful()

    def login(self, email: str, password: Union[int, str], mode: LoginMode = LoginMode.PASSWORD) -> bool:
        """
        Attempts to generate Session ID by trying to log in as a StepN user
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
                return self.do_code_check(self.get_auth_code())
            else:
                return True
        # reset session ID
        self.session_id = None
        return False

    def run(self, _command: str, **parameters) -> Optional[Response]:
        parameters["sessionID"] = self.session_id
        url = self.__url_prefix + _command
        web_response = self.session.get(url, params=parameters)

        try:
            response = Response(web_response.json())
        except JSONDecodeError:
            logging.error(f"Error occurred while accessing {url}:\n{web_response.text}")
            return None

        return response

    def do_code_check(self, code: JsonNumber) -> bool:
        response = self.run('doCodeCheck', codeData=f"2:{code}")
        return response and response.is_successful()

    def userbasic(self) -> Response:
        return self.run("userbasic")

    def order_data(self, order_id: JsonNumber) -> Dict:
        response = self.run("orderdata", orderId=order_id)
        return response.get_data() if response else {}

    def buy_prop(self, order_id: JsonNumber, price: JsonNumber) -> bool:
        response = self.run("buyprop", orderID=order_id, price=price)
        return response and response.is_successful()

    def sell_prop(self, prop_id: JsonNumber, price: JsonNumber) -> Optional[Order]:
        response = self.run("addprop", propID=prop_id, price=price, googleCode=self.get_auth_code())
        order_id = response.get_data() if response else None
        if order_id:
            return Order(self, order_id)

    def cancel_order(self, order_id: JsonNumber):
        response = self.run("ordercancel", orderId=order_id)
        return response and response.is_successful()

    def change_price(self, order_id: JsonNumber, new_price: JsonNumber):
        response = self.run("changeprice", orderId=order_id, price=new_price)
        return response and response.is_successful()

    # lists
    def list_mystery_boxes(self):
        response = self.run('boxlist')
        return response.get_data() if response else []

    def list_bags(self):
        response = self.run("baglist")
        return response.get_data() if response else []

    def list_shoes(self, page: JsonNumber, do_refresh: bool):
        response = self.run("shoelist", page=page, refresh=do_refresh)
        return response.get_data() if response else []

    def list_orders(self, **order_query) -> List:
        response = self.run("orderlist", **order_query)
        return response.get_data() if response else []
