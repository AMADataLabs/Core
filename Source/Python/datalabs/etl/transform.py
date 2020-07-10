""" Transformer base class and NO-OP implementation. """
from abc import ABC, abstractmethod

from datalabs.etl.task import ETLTaskComponent


class Transformer(ETLTaskComponent, ABC):
    @abstractmethod
    def transform(self, data: "Extracted Data") -> 'Transformed Data':
        pass


class PassThroughTransformer(Transformer):
    def transform(self, data):
        return data
