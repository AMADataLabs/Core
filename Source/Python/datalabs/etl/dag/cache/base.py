''' Task data cache interface classes. '''
from   abc import ABC, abstractmethod
from   enum import Enum
import re

from   datalabs.plugin import import_plugin


class CacheDirection(Enum):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"


class TaskDataCache(ABC):
    def __init__(self, cache_parameters):
        self._parameters = cache_parameters

    @abstractmethod
    def extract_data(self) -> "list<bytes>":
        return None

    @abstractmethod
    def load_data(self, output_data: "list<bytes>"):
        pass


class TaskDataCacheParameters:
    @classmethod
    def extract(cls, task_parameters: dict) -> (dict, dict):
        cache_parameters = {}

        cache_parameters[CacheDirection.INPUT] = cls._get_cache_parameters(
            task_parameters,
            CacheDirection.INPUT
        )
        cache_parameters[CacheDirection.OUTPUT] = cls._get_cache_parameters(
            task_parameters,
            CacheDirection.OUTPUT
        )
        # cache_keys = [key for key in task_parameters if key.startswith('CACHE_')]

        return cache_parameters

    @classmethod
    def _get_cache_parameters(cls, task_parameters: dict, direction: CacheDirection) -> dict:
        cache_parameters = {}

        for key, value in task_parameters.items():
            cache_parameters.update(cls._extract_cache_parameter(direction, key, value))

        if cache_parameters and "execution_time" in task_parameters:
            cache_parameters["execution_time"] = task_parameters["execution_time"]

        return cache_parameters

    @classmethod
    def _extract_cache_parameter(cls, direction: CacheDirection, key: str, value: str):
        other_direction = [d[1] for d in CacheDirection.__members__.items() if d[1] != direction][0]  # pylint: disable=no-member
        cache_parameter = {}

        match = re.match(f'CACHE_({direction.value}_)?(..*)', key)

        if match and not match.group(2).startswith(other_direction.value+'_'):
            cache_parameter[match.group(2)] = value

        return cache_parameter


class TaskDataCacheFactory:
    @classmethod
    def create_cache(cls, direction: CacheDirection, cache_parameters: dict) -> TaskDataCache:
        cache_parameters = cache_parameters[direction]
        plugin = None

        if len(cache_parameters) > 1:
            plugin_name = 'datalabs.etl.dag.cache.s3.S3TaskDataCache'

            if 'CLASS' in cache_parameters:
                plugin_name = cache_parameters.pop('CLASS')

            TaskDataCachePlugin = import_plugin(plugin_name)  # pylint: disable=invalid-name

            plugin = TaskDataCachePlugin(cache_parameters)

        return plugin
