from json import dump, load
from os import getenv
from typing import *
from typing import Optional

from main import client
from stepn.client import Client


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
        return self.get_property_or_run(key, lambda x: default)

    def get_property_or_run(self, key: str, callback: Callable[[str], Any]) -> Any:
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

    def drop_property(self, key) -> None:
        self.__dictionary.pop(key)

    def save(self, file_path=__default_path) -> bool:
        try:
            with open(file_path, 'w') as file:
                dump(self.__dictionary, file)
                return True
        except FileNotFoundError:
            return False


def prompt(prompt_message: str):
    def prompt_fun():
        return input(prompt_message)

    return prompt_fun


def login(anonymous: bool = True) -> Optional[Client]:
    if anonymous:
        new_client = Client()
        email = input("Enter user E-Mail:")
        password = input("Enter user password:")

        if new_client.login(email, password, prompt("Enter Google authenticator code:")):
            return new_client

    else:
        env = Environment()
        new_client = Client(env.get_property("sessionID"))
        if new_client.ping():
            return client
        else:
            # couldn't log in with session ID
            email = env.get_property_or_run("email", prompt("Enter user E-Mail:"))
            password = env.get_property_or_run("password", prompt("Enter user password:"))

            if new_client.login(email, password, prompt("Enter Google authenticator code:")):
                env.set_property("email", email)
                env.set_property("password", password)
                env.set_property("sessionID", new_client.session_id)
                env.save()
                return client
            return None
