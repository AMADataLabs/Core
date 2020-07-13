""" Loader base class """
import logging

from abc import ABC, abstractmethod

from datalabs.etl.task import ETLComponentTask


class LoaderTask(ETLComponentTask, ABC):
    def run(self):
        self._data = self._parameters['data']

        self._load(self._data)

    @abstractmethod
    def _load(self, data: "Transformed Data"):
        pass


class ConsoleLoaderTask(LoaderTask):
    def __init__(self, parameters):
        super().__init__(parameters)

        self._logger = logging.getLogger(ConsoleLoader.__name__)
        self._logger.setLevel(logging.INFO)

    def _load(self, data):
        for datum in data:
            self._logger.info(datum)

