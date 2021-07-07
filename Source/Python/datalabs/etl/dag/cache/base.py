''' Task data cache interface classes. '''
from   abc import ABC, abstractmethod
from   enum import Enum


class CacheDirection(Enum):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"


class TaskDataCache(ABC):
    def __init__(self, cache_parameters):
        self._parameters = cache_parameters

    @abstractmethod
    def extract_data(self):
        return None

    @abstractmethod
    def load_data(self, output_data):
        pass
