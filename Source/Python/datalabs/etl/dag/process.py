''' Classes for processing DAG scheduler events. '''
from   dataclasses import dataclass
import logging

from   datalabs.access.aws import AWSClient
from   datalabs.task import Task
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
class DAGProcessorParameters:
    dag: str='DAG_SCHEDULER'  # default is to run the DAG Scheduler DAG


class DAGProcessorTask(Task):
    PARAMETER_CLASS = DAGProcessorParameters

    def run(self):
        LOGGER.debug('DAG Processor Parameters: %s', self._parameters)

        with AWSClient("lambda") as awslambda:
            awslambda.invoke(
                FunctionName='string',
                InvocationType='Event',
                Payload='parameters'
            )


@add_schema
@dataclass
class TaskProcessorParameters:
    dag: str
    task: str
    dag_class: type
    state_class: type


class TaskProcessorTask(Task):
    PARAMETER_CLASS = TaskProcessorParameters

    def run(self):
        LOGGER.debug('Task Processor Parameters: %s', self._parameters)
