from typing import Optional, Union


class Response:

    def __init__(self, src: dict):
        self._status = src['code']
        self._data = src['data'] if 'data' in src else None
        self._message = src['msg'] if 'msg' in src else None

    def is_successful(self) -> bool:
        return self._status == 0

    def get_message(self) -> Optional[str]:
        return self._message

    def get_data(self) -> Optional[Union[dict, list]]:
        return self._data or None
