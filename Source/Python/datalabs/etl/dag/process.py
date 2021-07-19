''' Classes for processing DAG scheduler events. '''
from   dataclasses import dataclass
import logging

from   datalabs.task import Task
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema(unknowns=True)
@dataclass
class DAGProcessorParameters:
    dag: str
    execution_time: str
    dag_class: str
    dag_state_class: str
    unknowns: dict=None


class DAGProcessorTask(Task):
    PARAMETER_CLASS = DAGProcessorParameters

    def run(self):
        LOGGER.debug('DAG Processor Parameters: %s', self._parameters)


@add_schema(unknowns=True)
@dataclass
class TaskProcessorParameters:
    dag: str
    task: str
    execution_time: str
    dag_class: str
    dag_state_class: str
    unknowns: dict=None


class TaskProcessorTask(Task):
    PARAMETER_CLASS = TaskProcessorParameters

    def run(self):
        LOGGER.debug('Task Processor Parameters: %s', self._parameters)
