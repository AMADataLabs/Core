from abc import ABC, abstractmethod


class Transformer:
    def __init__(self, configuration):
        self._configuration = configuration

    @abstractmethod
    def transform(self, data: "Extracted Data") -> 'Transformed Data':
        pass


class PassThroughTransformer:
    def transform(self, data):
        return data