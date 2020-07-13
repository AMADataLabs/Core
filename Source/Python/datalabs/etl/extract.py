""" Extractor base class """
from abc import ABC, abstractmethod

from datalabs.task import Task


class ExtractorTask(Task, ABC):
    def run(self):
        self._data = self._extract()

    @abstractmethod
    def _extract(self) -> "Extracted Data":
        pass
