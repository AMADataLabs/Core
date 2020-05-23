from abc import ABC, abstractmethod


class Loader:
    def __init__(self, configuration):
        self._configuration = configuration

    @abstractmethod
    def load(self, data: "Transformed Data"):
        pass
