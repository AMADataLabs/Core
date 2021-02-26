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
    Input = "INPUT"
    Output = "OUTPUT"


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
    def _get_task_parameters(self):
        parameters = self._get_dag_task_parameters()
        cache_plugin = self._get_cache_plugin(parameters, CacheDirection.Input)
        input_data = cache_plugin.extract_data()

        parameters['data'] = input_data

        return parameters

    def _handle_exception(self, exception: etl.ETLException):
        LOGGER.exception('Handling Airflow task exception: %s', exception)

    def _handle_success(self):
        cache_plugin = self._get_cache_plugin(self._task_parameters, CacheDirection.Output)  # pylint: disable=no-member
        cache_plugin.load_data(self.task.data)

        LOGGER.info('Airflow task has finished')

    def _get_dag_task_parameters(self, ):
        args = self._parameters
        dag_id, task_id, datestamp = args[1].split('__')
        dag_parameters = self._get_dag_parameters_from_environment(dag_id.upper(), datestamp)
        task_parameters = self._get_task_parameters_from_environment(dag_id.upper(), task_id.upper())

        return self._merge_parameters(dag_parameters, task_parameters)

    @classmethod
    def _get_cache_plugin(cls, task_parameters: dict, direction: CacheDirection) -> TaskDataCache:
        cache_parameters = cls._get_cache_parameters(task_parameters, direction)
        plugin_name = 'datalabs.etl.airflow.s3.S3TaskDataCache'

        if 'CLASS' in cache_parameters:
            plugin_name = cache_parameters.pop('CLASS')

        TaskDataCachePlugin = import_plugin(plugin_name)  # pylint: disable=invalid-name

        return TaskDataCachePlugin(cache_parameters)

    @classmethod
    def _get_dag_parameters_from_environment(cls, dag_id, datestamp):
        parameters = cls._get_parameters([dag_id.upper()])

        parameters['EXECUTION_TIME'] = datestamp
        parameters['CACHE_EXECUTION_TIME'] = datestamp

        return parameters

    @classmethod
    def _get_task_parameters_from_environment(cls, dag_id, task_id):
        parameters = cls._get_parameters([dag_id.upper(), task_id.upper()])

        return parameters

    @classmethod
    def  _merge_parameters(cls, dag_parameters, task_parameters):
        parameters = dag_parameters

        parameters.update(task_parameters)

        return parameters

    @classmethod
    def _get_cache_parameters(cls, task_parameters: dict, direction: CacheDirection) -> dict:
        cache_parameters = {}

        for key, value in task_parameters.items():
            match = re.match(f'CACHE_({direction.value}_)?(..*)', key)

            if match:
                cache_parameters[match.group(2)] = value

        return cache_parameters

    @classmethod
    def _get_parameters(cls, branch):
        var_tree = VariableTree.generate()

        return var_tree.get_branch_values(branch)
