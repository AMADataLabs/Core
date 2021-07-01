""" DAG runner task class. """
from   dataclasses import dataclass
import logging

import paradag

from   datalabs.access.aws import AWSClient
from   datalabs.etl.dag.state import Status
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class DAGSchedulerRunnerTask(Task):
    # pylint: disable=no-self-use
    def run(self):
        with AWSClient("sns") as sns:
            sns.publish(
                TopicArn=os.environ.get("DAG_TOPIC_ARN"),
                Message=json.dumps(dict(DAG_CLASS="datalabs.etl.dag.schedule.DAGSchedulerTask", ))
            )


@add_schema
@dataclass
class DAGProcessorParameters:
    dag_class: type
    state_class: type


class DAGProcessorTask(Task):
    PARAMETER_CLASS = DAGProcessorParameters

    def run(self):
        LOGGER.debug('DAG Processor Parameters: %s', self._parameters)


@add_schema
@dataclass
class TaskProcessorParameters:
    dag_class: type
    state_class: type
    task: str


class TaskProcessorTask(Task):
    PARAMETER_CLASS = TaskProcessorParameters

    def run(self):
        LOGGER.debug('Task Processor Parameters: %s', self._parameters)


@add_schema
@dataclass
class DAGExecutorParameters:
    dag_class: type
    state_class: type


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
