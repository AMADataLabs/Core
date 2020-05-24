""" Transformer base class and NO-OP implementation. """
from abc import ABC, abstractmethod


class Transformer(ABC):
    def __init__(self, configuration):
        self._configuration = configuration

    @abstractmethod
    def transform(self, data: "Extracted Data") -> 'Transformed Data':
        pass


class PassThroughTransformer(Transformer):
    def transform(self, data):
        return data
