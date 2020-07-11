""" Transformer base class and NO-OP implementation. """
from abc import ABC, abstractmethod

from datalabs.task import Task


class TransformerTask(Task, ABC):
    @abstractmethod
    def transform(self, data: "Extracted Data") -> 'Transformed Data':
        pass


class PassThroughTransformerTask(TransformerTask):
    def transform(self, data):
        return data
