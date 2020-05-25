""" Loader base class """
import logging

from abc import ABC, abstractmethod


class Loader(ABC):
    def __init__(self, configuration):
        self._configuration = configuration

    @abstractmethod
    def load(self, data: "Transformed Data"):
        pass


class ConsoleLoader(Loader):
    def __init__(self, configuration):
        super().__init__(configuration)

        self._logger = logging.getLogger(ConsoleLoader.__name__)
        self._logger.setLevel(logging.INFO)

    def load(self, data):
        for datum in data:
            self._logger.info(datum)

