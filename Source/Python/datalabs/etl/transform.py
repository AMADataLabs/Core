""" Transformer base class and NO-OP implementation. """
from abc import ABC, abstractmethod

from datalabs.task import Task


class TransformerTask(Task, ABC):
    def run(self):
        self._data = self._transform(parameters['data'])

    @abstractmethod
    def _transform(self, data: "Extracted Data") -> 'Transformed Data':
        pass


class PassThroughTransformerTask(TransformerTask):
    def _transform(self, data):
        return data
