""" Extractor base class """
from abc import ABC, abstractmethod

from datalabs.etl.task import ETLComponentTask


class ExtractorTask(ETLComponentTask, ABC):
    def run(self):
        self._data = self._extract()

    @abstractmethod
    def _extract(self) -> "Extracted Data":
        pass
