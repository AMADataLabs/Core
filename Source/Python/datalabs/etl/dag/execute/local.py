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
    execution_time: str
    dag_class: str
    dag_state_class: str
    unknowns: dict=None


class LocalDAGExecutorTask(Task):
    PARAMETER_CLASS = LocalDAGExecutorParameters

    def run(self):
        dag = import_plugin(self._parameters.dag_class)()
        # TODO: set the DAG state based on task states
        # dag_state = import_plugin(self._parameters.dag_state_class)(self._get_state_parameters())

        paradag.dag_run(
            dag,
            processor=paradag.MultiThreadProcessor(),
            executor=self
        )

    # pylint: disable=no-self-use
    def param(self, task: 'DAGTask'):
        return task

    # pylint: disable=assignment-from-no-return
    def execute(self, task):
        state = self._get_task_status(task)

        if state == Status.UNKNOWN and task.ready:
            self._trigger_task(task)

        return state

    # pylint: disable=no-self-use
    def deliver(self, task, predecessor_result):
        if predecessor_result != Status.FINISHED:
            task.block()

    # pylint: disable=no-self-use, fixme
    def _get_task_status(self, task):
        # TODO: get state using task state plugin
        state = import_plugin(self._parameters.dag_state_class)(self._get_state_parameters(task.id))
        status = state.get_task_status(self._parameters.dag, task.id, self._parameters.execution_time)

        LOGGER.info('State of task "%s" of DAG "%s": %s', task.id, self._parameters.dag, status)

        return status

    # pylint: disable=no-self-use, fixme
    def _trigger_task(self, task):
        # TODO: send message using messaging plugin
        LOGGER.info('Triggering task "%s" of DAG "%s"', task.id, self._parameters.dag)

    def _get_state_parameters(self, task=None):
        state_parameters = self._parameters.unknowns

        state_parameters["execution_time"] = self._parameters.execution_time
        state_parameters["dag"] = self._parameters.dag

        if task:
            state_parameters["task"] = task

        return state_parameters
