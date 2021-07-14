''' Classes for executing DAG objects '''
from   dataclasses import dataclass

import paradag

from   datalabs.etl.dag.state import Status
from   datalabs.parameter import add_schema
from   datalabs.plugin import import_plugin
from   datalabs.task import Task


@add_schema(unknowns=True)
@dataclass
class DAGExecutorParameters:
    dag_class: type
    dag_state_class: type
    unknowns: dict=None


class DAGExecutorTask(Task):
    PARAMETER_CLASS = DAGExecutorParameters

    def run(self):
        dag = import_plugin(self._parameters.dag_class)()
        dag_state = import_plugin(self._parameters.dag_state_class)(self._parameters.unknowns)

        paradag.dag_run(
            dag,
            processor=paradag.MultiThreadProcessor(),
            executor=DAGExecutor(dag_state)
        )


class DAGExecutor:
    def __init__(self, dag_state):
        self._state = dag_state

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
