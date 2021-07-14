''' Classes for executing DAGs and DAG tasks locally '''
from   dataclasses import dataclass
import logging

import paradag

from   datalabs.etl.dag.state import Status
from   datalabs.parameter import add_schema
from   datalabs.plugin import import_plugin
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema(unknowns=True)
@dataclass
class LocalDAGExecutorParameters:
    dag: str
    dag_class: str
    dag_state_class: str
    execution_time: str
    unknowns: dict=None

class LocalDAGExecutorTask(Task):
    PARAMETER_CLASS = LocalDAGExecutorParameters

    def run(self):
        dag = import_plugin(self._parameters.dag_class)()
        state_parameters = self._get_state_parameters()
        dag_state = import_plugin(self._parameters.dag_state_class)(self._parameters.unknowns)

        paradag.dag_run(
            dag,
            processor=paradag.MultiThreadProcessor(),
            executor=DAGExecutor(self._parameters.dag, self._parameters.execution_time, dag_state)
        )

    def _get_state_parameters(self):
        state_parameters = self._parameters.unknowns

        state_parameters["execution_time"] = self._parameters.execution_time
        state_parameters["dag"] = self._parameters.dag


class DAGExecutor:
    def __init__(self, dag, execution_time, dag_state):
        self._dag = dag
        self._execution_time = execution_time
        self._state = dag_state

    # pylint: disable=no-self-use
    def param(self, task: 'DAGTask'):
        return task

    # pylint: disable=assignment-from-no-return
    def execute(self, task):
        state = self._get_task_state(task)

        if state == Status.UNKNOWN and task.ready:
            self._trigger_task(task)

        return state

    # pylint: disable=no-self-use
    def deliver(self, task, predecessor_result):
        if predecessor_result != Status.FINISHED:
            task.block()

    # pylint: disable=no-self-use, fixme
    def _get_task_state(self, task):
        # TODO: get state using task state plugin
        state = self._state.get_status()

        LOGGER.info('State of task "%s" of DAG "%s": %s', task.id, self._dag, state)

        return state

    # pylint: disable=no-self-use, fixme
    def _trigger_task(self, task):
        # TODO: send message using messaging plugin
        LOGGER.info('Triggering task "%s" of DAG "%s"', task.id, self._dag)
