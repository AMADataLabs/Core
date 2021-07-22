''' Classes for processing DAG scheduler events. '''
from   dataclasses import dataclass
import logging

from   datalabs.etl.dag.state import Status
import datalabs.feature
from   datalabs.parameter import add_schema
from   datalabs.plugin import import_plugin
from   datalabs.task import Task

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
    dag_executor_class: str
    unknowns: dict=None


class DAGProcessorTask(Task):
    PARAMETER_CLASS = DAGProcessorParameters

    def run(self):
        LOGGER.debug('DAG Processor Parameters: %s', self._parameters)

        if datalabs.feature.enabled("DL1902"):
            plugin_parameters = self._get_plugin_parameters()

            state = import_plugin(self._parameters.dag_state_class)(plugin_parameters)
            executor = import_plugin(self._parameters.dag_executor_class)(plugin_parameters)

            status = state.get_dag_status(self._parameters.dag, self._parameters.execution_time)

            if status == Status.UNKNOWN:
                state.set_dag_status(self._parameters.dag, self._parameters.execution_time, Status.PENDING)

            executor.run()


        # DAG plugin parameters for running a DAG:
        # {
        #   "dag": "string"
        #   "type": "DAG",
        #   "execution_time": "time"
        # }

    def _get_plugin_parameters(self):
        parameters = self._parameters.unknowns or {}

        parameters.update()

        return parameters


@add_schema(unknowns=True)
@dataclass
class TaskProcessorParameters:
    dag: str
    task: str
    execution_time: str
    dag_class: str
    dag_state_class: str
    dag_executor_class: str
    unknowns: dict=None


class TaskProcessorTask(Task):
    PARAMETER_CLASS = TaskProcessorParameters

    def run(self):
        LOGGER.debug('Task Processor Parameters: %s', self._parameters)

        # DAG plugin parameters for running a task:
        # {
        #   "dag": "string"
        #   "type": "Task",
        #   "task": "string",
        #   "execution_time": "time"
        # }
