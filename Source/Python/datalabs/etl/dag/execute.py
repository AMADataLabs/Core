''' Classes for executing DAG objects '''
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
class DAGExecutorParameters:
    dag: str
    dag_class: str
    dag_state_class: str
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
        state = Status.UNKNOWN

        LOGGER.info('Task "%s" state: %s', task.id, state)

        return state

    # pylint: disable=no-self-use, fixme
    def _trigger_task(self, task):
        # TODO: send message using messaging plugin
        LOGGER.info('Triggering task "%s"', task.id)
