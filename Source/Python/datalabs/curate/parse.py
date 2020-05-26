""" Parser abstract base class """
import pandas

from abc import ABC, abstractmethod


class Parser(ABC):
    @abstractmethod
    def parse(self, text: str) -> pandas.DataFrame:
        pass
