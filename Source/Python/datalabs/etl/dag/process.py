''' Classes for processing DAG scheduler events. '''
from   dataclasses import dataclass
import logging

from   datalabs.etl.dag.state import Status
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
        state = self._get_plugin(self._parameters.dag_state_class, self._parameters)
        executor = self._get_plugin(self._parameters.dag_executor_class, self._parameters)

        status = state.get_dag_status(self._parameters.dag, self._parameters.execution_time)
        LOGGER.info('DAG %s Status: %s', self._parameters.dag, status.value)

        if status == Status.UNKNOWN:
            state.set_dag_status(self._parameters.dag, self._parameters.execution_time, Status.PENDING)

        executor.run()

    @classmethod
    def _get_plugin(cls, plugin_class_name, task_parameters):
        plugin_class = import_plugin(plugin_class_name)
        plugin_parameters = cls._get_plugin_parameters(plugin_class, task_parameters)
        LOGGER.debug('%s Plugin Parameters: %s', plugin_class.__name__, plugin_parameters)

        return plugin_class(plugin_parameters)

    @classmethod
    def _get_plugin_parameters(cls, plugin_class: type, task_parameters):
        fields = plugin_class.PARAMETER_CLASS.__dataclass_fields__.keys()
        parameters = {key:getattr(task_parameters, key) for key in task_parameters.__dataclass_fields__.keys()}

        if hasattr(task_parameters, "unknowns"):
            cls._merge_parameter_unknowns(parameters)
        else:
            cls._remove_unknowns(parameters, fields)

        return parameters

    @classmethod
    def _merge_parameter_unknowns(cls, parameters):
        unknowns = parameters.get("unknowns", {})
        parameters.update(unknowns)
        parameters.pop("unknowns")

    @classmethod
    def _remove_unknowns(cls, parameters, fields):
        for key in parameters:
            if key not in fields:
                parameters.pop(key)


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
