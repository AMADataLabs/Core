""" Parser abstract base class """
import io

import pandas

from abc import ABC, abstractmethod


class Parser(ABC):
    @abstractmethod
    def parse(self, text: str) -> pandas.DataFrame:
        pass


class CSVParser(ABC):
    def parse(self, text: str) -> pandas.DataFrame:
        return pandas.read_csv(io.StringIO(text))
