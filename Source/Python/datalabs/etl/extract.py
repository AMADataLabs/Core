""" Extractor base class """
from abc import ABC, abstractmethod

from datalabs.etl.task import ETLTaskComponent


class Extractor(ETLTaskComponent, ABC):
    @abstractmethod
    def extract(self) -> "Extracted Data":
        pass
