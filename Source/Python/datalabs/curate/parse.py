""" Parser abstract base class """
from   abc import ABC, abstractmethod
import io

import pandas


class Parser(ABC):
    @abstractmethod
    def parse(self, text: str) -> pandas.DataFrame:
        pass


class PassThroughParser(Parser):
    # pylint: disable=no-self-use
    def parse(self, text: str) -> pandas.DataFrame:
        return text


class CSVParser(Parser):
    # pylint: disable=no-self-use
    def parse(self, text: str) -> pandas.DataFrame:
        return pandas.read_csv(io.StringIO(text))
