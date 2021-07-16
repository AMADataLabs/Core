""" DAG task wrapper and runner classes. """
import logging
import re

from   datalabs.access.environment import VariableTree
from   datalabs.etl.dag.cache import CacheDirection, TaskDataCache
from   datalabs.plugin import import_plugin
from   datalabs.task import TaskWrapper

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# FIXME: handle running DAGs as well
class DAGTaskWrapper(TaskWrapper):
    def __init__(self, parameters=None):
        super().__init__(parameters)

        self._cache_parameters = {}

    # pylint: disable=no-self-use
    def _get_runtime_parameters(self, parameters):
        dag, task, execution_time = parameters[1].split('__')

        return dict(
            dag=dag,
            task=task,
            execution_time=execution_time
        )

    def _get_task_parameters(self):
        task_parameters = None
        import pdb; pdb.set_trace()

        default_parameters = self._get_default_parameters()

        task_parameters = self._merge_parameters(default_parameters, self._get_dag_task_parameters())

        task_parameters = self._extract_cache_parameters(task_parameters)

        cache_plugin = self._get_cache_plugin(CacheDirection.INPUT)
        if cache_plugin:
            input_data = cache_plugin.extract_data()

            task_parameters['data'] = input_data

        return task_parameters

    def _handle_exception(self, exception):
        LOGGER.exception('Handling DAG task exception: %s', exception)

    def _handle_success(self):
        cache_plugin = self._get_cache_plugin(CacheDirection.OUTPUT)  # pylint: disable=no-member
        if cache_plugin:
            cache_plugin.load_data(self.task.data)

        LOGGER.info('DAG task has finished')

    def _get_default_parameters(self):
        dag_parameters = self._get_default_parameters_from_environment(self._get_dag_id())
        execution_time = self._get_execution_time()

        dag_parameters['EXECUTION_TIME'] = execution_time
        dag_parameters['CACHE_EXECUTION_TIME'] = execution_time

        return dag_parameters

    def _get_dag_task_parameters(self):
        return self._get_task_parameters_from_environment(self._get_dag_id(), self._get_task_id())

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
            plugin_name = 'datalabs.etl.dag.cache.s3.S3TaskDataCache'

            if 'CLASS' in cache_parameters:
                plugin_name = cache_parameters.pop('CLASS')

            TaskDataCachePlugin = import_plugin(plugin_name)  # pylint: disable=invalid-name

            plugin = TaskDataCachePlugin(cache_parameters)

        return plugin

    def _get_dag_id(self):
        return self._runtime_parameters["dag"].upper()

    def _get_task_id(self):
        return self._runtime_parameters["task"].upper()

    def _get_execution_time(self):
        return self._runtime_parameters["execution_time"].upper()

    @classmethod
    def _get_default_parameters_from_environment(cls, dag_id):
        parameters = {}

        try:
            parameters = cls._get_parameters([dag_id.upper()])
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
        var_tree = VariableTree.from_environment()

        candidate_parameters = var_tree.get_branch_values(branch)

        return {key:value for key, value in candidate_parameters.items() if value is not None}
