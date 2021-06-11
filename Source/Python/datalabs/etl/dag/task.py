""" DAG runner task class. """
from   dataclasses import dataclass

import paradag

from   datalabs.etl.dag.state import State
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
        dag = dag_class()

        paradag.dag_run(
            dag,
            processor=paradag.MultiThreadProcessor(),
            executor=DAGExecutor(self._parameters.state_class)
        )


class DAGExecutor:
    def __init__(self, state_class: type):
        self._state = state_class()

    def param(self, task: 'DAGTask'):
        return task

    def execute(self, task):
        state = self._get_task_state(task)

        if state == State.UNKNOWN:
            self._trigger_task(task)

        return state

    def deliver(self, task, predecessor_result):
        if predecessor_result != State.FINISHED:
            task.block()

    def _get_task_state(self, task):
        pass

    def _trigger_task(self, task):
        pass
