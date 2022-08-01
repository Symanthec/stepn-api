import logging
from typing import Union, Callable, Dict, List, Optional

from requests import JSONDecodeError, Session

from .loginmode import LoginMode
from .passhash import PasswordHasher
from .response import Response
from ..order import Order
from ..typing import JsonNumber


class Client:
    __url_prefix = "https://api.stepn.com/run/"

    def __init__(self, auth_callback: Callable[[], str], new_session_id=None):
        self.get_auth_code = auth_callback
        self.session = Session()
        self.session_id = new_session_id

    def ping(self) -> bool:
        """ Requests basic user info. If response contains code 0, then sessionID is valid. """
        return self.userbasic() is not None

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

    def do_code_check(self, code: JsonNumber) -> bool:
        return self.run('doCodeCheck', codeData=f"2:{code}").is_successful()

    def userbasic(self) -> Response:
        return self.run("userbasic")

    def order_data(self, order_id: JsonNumber) -> Dict:
        return self.run("orderdata", orderId=order_id).get_data() or {}

    def buy_prop(self, order_id: JsonNumber, price: JsonNumber) -> bool:
        return self.run("buyprop", orderID=order_id, price=price).is_successful()

    def sell_prop(self, prop_id: JsonNumber, price: JsonNumber) -> Optional[Order]:
        order_id = self.run("addprop", propID=prop_id, price=price, googleCode=self.get_auth_code()).get_data()
        if order_id:
            return Order(self, order_id)

    def cancel_order(self, order_id: JsonNumber):
        return self.run("ordercancel", orderId=order_id).is_successful()

    def change_price(self, order_id: JsonNumber, new_price: JsonNumber):
        return self.run("changeprice", orderId=order_id, price=new_price).is_successful()

    # lists
    def list_mystery_boxes(self):
        return self.run("boxlist").get_data() or []

    def list_bags(self):
        return self.run("baglist").get_data() or []

    def list_shoes(self, page: JsonNumber, do_refresh: bool):
        return self.run("shoelist", page=page, refresh=do_refresh).get_data() or []

    def list_orders(self, **order_query) -> List:
        return self.run("orderlist", **order_query).get_data() or []
