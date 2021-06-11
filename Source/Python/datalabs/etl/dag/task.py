""" DAG runner task class. """
from   dataclasses import dataclass

import paradag

from   datalabs.etl.dag.state import Status
from   datalabs.parameter import add_schema
from   datalabs.task import Task


@add_schema
@dataclass
class DAGExecutorParameters:
    dag_class: type
    dag_state_class: type


class DAGExecutorTask(Task):
    PARAMETER_CLASS = DAGExecutorParameters

    def run(self):
        dag = self._parameters.dag_class()

        paradag.dag_run(
            dag,
            processor=paradag.MultiThreadProcessor(),
            executor=DAGExecutor(self._parameters.state_class)
        )


class DAGExecutor:
    def __init__(self, state_class: type):
        self._state = state_class()

    # pylint: disable=no-self-use
    def param(self, task: 'DAGTask'):
        return task

    # pylint: disable=assignment-from-no-return
    def execute(self, task):
        state = self._get_task_state(task)

        if state == Status.UNKNOWN:
            self._trigger_task(task)

        return state

    # pylint: disable=no-self-use
    def deliver(self, task, predecessor_result):
        if predecessor_result != Status.FINISHED:
            task.block()

    # pylint: disable=no-self-use, fixme
    def _get_task_state(self, task):
        # TODO: get state using task state plugin
        pass

    # pylint: disable=no-self-use, fixme
    def _trigger_task(self, task):
        # TODO: send message using messaging plugin
        pass
