""" DAG task wrapper and runner classes. """
from abc import abstractmethod
import logging

from   datalabs.access.environment import VariableTree
from   datalabs.etl.dag.cache import CacheDirection, TaskDataCacheParameters, TaskDataCacheFactory
from   datalabs.etl.dag.event import EventDrivenDAGMixin
from   datalabs.task import TaskWrapper

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class DAGTaskIDMixin:
    def _get_dag_id(self):
        return self._task_parameters["dag"].upper()

    def _get_dag_name(self):
        base_name, _ = self._parse_dag_id(self._get_dag_id())

        return base_name

    def _get_dag_index(self):
        _, index = self._parse_dag_id(self._get_dag_id())

        return index

    def _get_task_id(self):
        return self._task_parameters.get("task", "DAG").upper()

    def _get_execution_time(self):
        return self._task_parameters["execution_time"].upper()

    @classmethod
    def _parse_dag_id(cls, dag):
        base_name = dag
        iteration = None
        components = dag.split(':')

        if len(components) == 2:
            base_name, iteration = components

        return base_name, iteration


class DAGTaskWrapper(DAGTaskIDMixin, EventDrivenDAGMixin, TaskWrapper):
    def __init__(self, parameters=None):
        super().__init__(parameters)

        self._cache_parameters = {}

    def _get_task_parameters(self):
        task_parameters = None

        task_parameters = self._get_dag_parameters()

        task_parameters.update(self._get_dag_task_parameters())

        self._cache_parameters = self._extract_cache_parameters(task_parameters)
        LOGGER.debug('Task Parameters: %s', task_parameters)

        return task_parameters

    def _get_task_input_data(self):
        data = []
        cache = TaskDataCacheFactory.create_cache(CacheDirection.INPUT, self._cache_parameters)

        if cache:
            data = cache.extract_data()

        return data

    def _put_task_output_data(self, data):
        cache = TaskDataCacheFactory.create_cache(CacheDirection.OUTPUT, self._cache_parameters)

        if cache:
            cache.load_data(data)

    def _handle_success(self) -> str:
        super()._handle_success()

        if self._get_task_id() == "DAG":
            self._handle_dag_success(self.task)
        else:
            self._handle_task_success(self.task)

        return "Success"

    def _handle_exception(self, exception) -> str:
        super()._handle_exception(exception)

        if self._get_task_id() == "DAG":
            self._handle_dag_exception(self.task)
        else:
            self._handle_task_exception(self.task)

        return f'Failed: {str(exception)}'

    @abstractmethod
    def _get_dag_parameters(self):
        return {}

    def _get_dag_task_parameters(self):
        parameters = {}

        try:
            parameters = self._get_parameters_from_environment(self._get_dag_id().upper(), self._get_task_id().upper())
        except KeyError:
            pass

        return parameters

    @classmethod
    def _extract_cache_parameters(cls, task_parameters):
        return TaskDataCacheParameters.extract(task_parameters)

    @classmethod
    def _get_parameters_from_environment(cls, dag, task):
        var_tree = VariableTree.from_environment()

        candidate_parameters = var_tree.get_branch_values([dag, task])

        return {key:value for key, value in candidate_parameters.items() if value is not None}
