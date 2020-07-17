""" Transformer base class and NO-OP implementation. """
from abc import ABC, abstractmethod

from datalabs.etl.task import ETLComponentTask


class TransformerTask(ETLComponentTask, ABC):
    def run(self):
        self._data = self._transform()

    @abstractmethod
    def _transform(self) -> 'Transformed Data':
        pass


class PassThroughTransformerTask(TransformerTask):
    def _transform(self):
        return self._parameters.data
