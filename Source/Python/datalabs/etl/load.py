""" Loader base class """
import logging

from abc import ABC, abstractmethod

from datalabs.etl.task import ETLTaskComponent


class Loader(ETLTaskComponent, ABC):
    @abstractmethod
    def load(self, data: "Transformed Data"):
        pass


class ConsoleLoader(Loader):
    def __init__(self, parameters):
        super().__init__(parameters)

        self._logger = logging.getLogger(ConsoleLoader.__name__)
        self._logger.setLevel(logging.INFO)

    def load(self, data):
        for datum in data:
            self._logger.info(datum)

