''' TaskWrapper for Airflow tasks providing caching of task data. '''
from   abc import ABC, abstractmethod
from   enum import Enum
import logging
import re

from   datalabs.access.environment import VariableTree
import datalabs.etl.task as etl
from   datalabs.plugin import import_plugin
import datalabs.task as task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


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


class AirflowTaskWrapper(task.TaskWrapper):
    def __init__(self, parameters=None):
        super().__init__(parameters)

        args = self._parameters
        self._dag_id, self._task_id, self._datestamp = args[1].split('__')

        self._cache_parameters = {}

    def _get_task_parameters(self):
        parameters = self._get_dag_task_parameters()
        parameters = self._extract_cache_parameters(parameters)

        cache_plugin = self._get_cache_plugin(CacheDirection.INPUT)
        if cache_plugin:
            input_data = cache_plugin.extract_data()

            parameters['data'] = input_data

        return parameters

    def _handle_exception(self, exception: etl.ETLException):
        LOGGER.exception('Handling Airflow task exception: %s', exception)

    def _handle_success(self):
        cache_plugin = self._get_cache_plugin(CacheDirection.OUTPUT)  # pylint: disable=no-member
        if cache_plugin:
            cache_plugin.load_data(self.task.data)

        LOGGER.info('Airflow task has finished')

    def _get_dag_task_parameters(self):
        dag_parameters = self._get_dag_parameters_from_environment(self._dag_id.upper(), self._datestamp)
        task_parameters = self._get_task_parameters_from_environment(self._dag_id.upper(), self._task_id.upper())

        return self._merge_parameters(dag_parameters, task_parameters)

    def _extract_cache_parameters(self, task_parameters):
        self._cache_parameters[CacheDirection.INPUT] = self._get_cache_parameters(
            task_parameters,
            CacheDirection.INPUT
        )
        self._cache_parameters[CacheDirection.OUTPUT] = self._get_cache_parameters(
            task_parameters,
            CacheDirection.OUTPUT
        )
        cache_keys = [key for key in task_parameters if key.startswith('CACHE_')]

        for key in cache_keys:
            task_parameters.pop(key)

        return task_parameters

    def _get_cache_plugin(self, direction: CacheDirection) -> TaskDataCache:
        cache_parameters = self._cache_parameters[direction]
        plugin = None

        if len(cache_parameters) > 1:
            plugin_name = 'datalabs.etl.airflow.s3.S3TaskDataCache'

            if 'CLASS' in cache_parameters:
                plugin_name = cache_parameters.pop('CLASS')

            TaskDataCachePlugin = import_plugin(plugin_name)  # pylint: disable=invalid-name

            plugin = TaskDataCachePlugin(cache_parameters)

        return plugin

    @classmethod
    def _get_dag_parameters_from_environment(cls, dag_id, datestamp):
        parameters = {}

        try:
            parameters = cls._get_parameters([dag_id.upper()])

            parameters['EXECUTION_TIME'] = datestamp
            parameters['CACHE_EXECUTION_TIME'] = datestamp
        except KeyError:
            pass

        return parameters

    @classmethod
    def _get_task_parameters_from_environment(cls, dag_id, task_id):
        parameters = {}

        try:
            parameters = cls._get_parameters([dag_id.upper(), task_id.upper()])
        except KeyError:
            pass

        return parameters

    @classmethod
    def  _merge_parameters(cls, dag_parameters, task_parameters):
        parameters = dag_parameters

        parameters.update(task_parameters)

        return parameters

    @classmethod
    def _get_cache_parameters(cls, task_parameters: dict, direction: CacheDirection) -> dict:
        cache_parameters = {}
        other_direction = [d[1] for d in CacheDirection.__members__.items() if d[1] != direction][0]  # pylint: disable=no-member

        for key, value in task_parameters.items():
            match = re.match(f'CACHE_({direction.value}_)?(..*)', key)

            if match and not match.group(2).startswith(other_direction.value+'_'):
                cache_parameters[match.group(2)] = value

        return cache_parameters

    @classmethod
    def _get_parameters(cls, branch):
        var_tree = VariableTree.generate()

        candidate_parameters = var_tree.get_branch_values(branch)

        return {key:value for key, value in candidate_parameters.items() if value is not None}
