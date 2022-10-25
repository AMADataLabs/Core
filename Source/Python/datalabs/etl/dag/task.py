""" DAG task wrapper and runner classes. """
import logging

from   datalabs.access.environment import VariableTree
from   datalabs.etl.dag.cache import CacheDirection, TaskDataCacheParameters, TaskDataCacheFactory
from   datalabs.task import TaskWrapper

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class DAGTaskWrapper(TaskWrapper):
    def __init__(self, parameters=None):
        super().__init__(parameters)

        self._cache_parameters = {}

    def _get_runtime_parameters(self, parameters):
        return self._parse_command_line_parameters(parameters)

    def _get_task_parameters(self):
        task_parameters = None

        default_parameters = self._get_default_parameters()

        task_parameters = self._merge_parameters(default_parameters, self._get_dag_task_parameters())

        task_parameters, self._cache_parameters = TaskDataCacheParameters.extract(task_parameters)
        LOGGER.debug('Task Parameters: %s', task_parameters)

        return task_parameters

    def _get_task_data(self):
        data = []
        cache = TaskDataCacheFactory.create_cache(CacheDirection.INPUT, self._cache_parameters)

        if cache:
            data = cache.extract_data()

        return data

    def _handle_exception(self, exception):
        LOGGER.exception('Handling DAG task exception: %s', exception)

    def _handle_success(self):
        cache = TaskDataCacheFactory.create_cache(CacheDirection.OUTPUT, self._cache_parameters)
        if cache:
            cache.load_data(self.task._data)

        LOGGER.info('DAG task has finished')

    @classmethod
    def _parse_command_line_parameters(cls, command_line_parameters):
        dag, task, execution_time = command_line_parameters[1].split('__')

        return dict(
            dag=dag,
            task=task,
            execution_time=execution_time
        )

    def _get_default_parameters(self):
        dag_parameters = self._get_default_parameters_from_environment(self._get_dag_id())
        execution_time = self._get_execution_time()

        dag_parameters['EXECUTION_TIME'] = execution_time
        dag_parameters['CACHE_EXECUTION_TIME'] = execution_time

        return dag_parameters

    def _get_dag_task_parameters(self):
        return self._get_task_parameters_from_environment(self._get_dag_id(), self._get_task_id())

    def _get_dag_id(self):
        return self._runtime_parameters["dag"].upper()

    def _get_dag_name(self):
        base_name, _ = self._parse_dag_id(self._get_dag_id())

        return base_name

    def _get_dag_index(self):
        _, index = self._parse_dag_id(self._get_dag_id())

        return index

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
    def _parse_dag_id(cls, dag):
        base_name = dag
        iteration = None
        components = dag.split(':')

        if len(components) == 2:
            base_name, iteration = components

        return base_name, iteration

    @classmethod
    def _get_parameters(cls, branch):
        var_tree = VariableTree.from_environment()

        candidate_parameters = var_tree.get_branch_values(branch)

        return {key:value for key, value in candidate_parameters.items() if value is not None}
