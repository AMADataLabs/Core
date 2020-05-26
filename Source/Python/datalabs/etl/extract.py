""" Extractor base class """
from abc import ABC, abstractmethod


class Extractor(ABC):
    def __init__(self, configuration):
        self._configuration = configuration

    @abstractmethod
    def extract(self) -> "Extracted Data":
        pass
