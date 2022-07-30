from json import load, dump
from os import getenv
from typing import Any, Optional, Callable


class Environment:
    __default_path = 'env.json'

    def __init__(self, file_path: str = __default_path):
        self.__dictionary = dict()
        try:
            with open(file_path) as json:
                additional = load(json)
                self.__dictionary.update(additional)
        except Exception:
            pass

    def get_property(self, key: str, default: Any = None) -> Optional[Any]:
        return self.get_property_or_run(key, lambda: default)

    def get_property_or_run(self, key: str, callback: Callable[[str], Any]) -> Optional[Any]:
        if key not in self.__dictionary:
            # try searching elsewhere
            if not self.update_property(key):
                self.__dictionary[key] = callback(key)
        return self.__dictionary[key]

    def update_property(self, key):
        if new_value := getenv(key):
            self.__dictionary[key] = new_value
        return new_value

    def set_property(self, key: str, value: Any) -> None:
        self.__dictionary[key] = value

    def save(self, file_path=__default_path) -> bool:
        try:
            with open(file_path, 'w') as file:
                dump(self.__dictionary, file)
                return True
        except FileNotFoundError:
            return False
