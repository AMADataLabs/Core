""" Extractor base class """
from abc import ABC, abstractmethod

from datalabs.task import Task


class ExtractorTask(Task, ABC):
    @abstractmethod
    def extract(self) -> "Extracted Data":
        pass
