""" Loader base class """
import logging

from abc import ABC, abstractmethod

from datalabs.etl.task import ETLComponentTask


class LoaderTask(ETLComponentTask, ABC):
    def run(self):
        self._data = self._parameters.data

        self._load()

    @abstractmethod
    def _load(self):
        pass


class ConsoleLoaderTask(LoaderTask):
    def __init__(self, parameters):
        super().__init__(parameters)

        self._logger = logging.getLogger(ConsoleLoaderTask.__name__)
        self._logger.setLevel(logging.INFO)

    def _load(self):
        try:
            for datum in self._parameters.data:
                self._logger.info(datum)
        except:
            self._logger.info(self._parameters.data)
