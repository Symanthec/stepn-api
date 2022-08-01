from .client import Client
from .typing import JsonNumber


class Order:

    def __init__(self, client: Client, order_id: int):
        self._client = client
        self._order_id = order_id

    def get_order_id(self):
        return self._order_id

    def cancel_order(self):
        return self._client.cancel_order(self._order_id)

    def change_price(self, new_price: JsonNumber) -> bool:
        return self._client.change_price(self._order_id, new_price)

    def order_info(self):
        return self._client.order_data(self._order_id)
