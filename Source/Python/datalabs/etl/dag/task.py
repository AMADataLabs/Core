""" DAG task wrapper and runner classes. """
import logging
import time

from   datalabs.access.aws import AWSClient
from   datalabs.access.environment import VariableTree
from   datalabs.etl.dag.event import EventDrivenDAGMixin
from   datalabs.etl.dag.state import Status
from   datalabs.poll import TaskNotReady
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


class DAGTaskWrapper(DAGTaskIDMixin, TaskWrapper, EventDrivenDAGMixin):
    def _get_task_parameters(self):
        task_parameters = None

        dag_parameters = self._get_dag_parameters()

        task_parameters = self._get_dag_task_parameters(dag_parameters)

        task_parameters = self._merge_parameters(dag_parameters, task_parameters)
        LOGGER.debug('Task Parameters: %s', task_parameters)

        return task_parameters

    def _handle_success(self) -> str:
        super()._handle_success()

        if self._get_task_id() == "DAG":
            self._handle_dag_success(self.task)
        else:
            self._handle_task_success(self.task)

        return "Success"

    def _handle_exception(self, exception) -> str:
        super()._handle_exception(exception)

        if isinstance(exception, TaskNotReady):
            self.add_pause_dag()
        if self._task_parameters and self._get_task_id() == "DAG":
            self._handle_dag_exception(self.task)
        else:
            self._handle_task_exception(self.task)

        return f'Failed: {str(exception)}'

    # pylint: disable=line-too-long, no-member
    def add_pause_dag(self):
        dag_id = self._get_dag_id()
        execution_time = self._get_execution_time()
        dag_state = self._get_state_plugin(self._task_parameters)

        with AWSClient('dynamodb', **self._connection_parameters()) as dynamodb:
            dynamodb.put_item(
                TableName=self._parameters.table,
                Item={'dag_id': {'S': dag_id}, 'execution_time': {'S': execution_time},'ttl': {'N': str(time.time()+60*15)}},
                ConditionExpression="attribute_not_exists(#r)"
            )

        dag_state.set_task_status(
            dag_id,
            self._get_task_id(),
            execution_time,
            Status.PAUSED
        )

    # pylint: disable=no-self-use
    def _get_dag_parameters(self):
        return {"dag": "LOCAL"}

    def _get_dag_task_parameters(self, dag_parameters):
        dag_id = dag_parameters["dag"].upper()
        dag, _ = self._parse_dag_id(dag_id)
        task = dag_parameters.get("task", "DAG").upper()
        parameters = {}

        try:
            parameters = self._get_parameters_from_environment(dag, task)
        except KeyError:
            pass

        return parameters

    # pylint: disable=no-self-use
    def _handle_dag_success(self, dag):
        LOGGER.info("DAG %s succeeded.", dag)

    # pylint: disable=no-self-use
    def _handle_task_success(self, task):
        LOGGER.info("Task %s succeeded.", task)

    # pylint: disable=no-self-use
    def _handle_dag_exception(self, dag):
        LOGGER.info("DAG %s failed.", dag)

    # pylint: disable=no-self-use
    def _handle_task_exception(self, task):
        LOGGER.info("Task %s failed.", task)

    @classmethod
    def _get_parameters_from_environment(cls, dag, task):
        var_tree = VariableTree.from_environment()

        candidate_parameters = var_tree.get_branch_values([dag, task])

        return {key:value for key, value in candidate_parameters.items() if value is not None}
