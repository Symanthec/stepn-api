from abc import ABCMeta, abstractmethod


class URLParams(metaclass=ABCMeta):

    @abstractmethod
    def compile(self) -> dict:
        pass