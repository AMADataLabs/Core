""" ETL DAG state classes """
from   abc import ABC, abstractmethod
from   enum import Enum
from   itertools import dropwhile
import json

from   datalabs.parameter import ParameterValidatorMixin
from   datalabs.plugin import import_plugin


class Status(Enum):
    UNKNOWN = 'Unknown'
    PENDING = 'Pending'
    RUNNING = 'Running'
    FINISHED = 'Finished'
    FAILED = 'Failed'

    # pylint: disable=no-member
    def __gt__(self, other):
        greater_than = False
        successors = [s[1] for s in dropwhile(lambda item: item[1] != other, self.__class__.__members__.items())][1:]

        if (other != Status.FINISHED) and self in successors:
            greater_than = True

        return greater_than


class State(ParameterValidatorMixin, ABC):
    PARAMETER_CLASS = None

    # pylint: disable=super-init-not-called
    def __init__(self, parameters: dict):
        self._parameters = parameters

        if self.PARAMETER_CLASS:
            self._parameters = self._get_validated_parameters(parameters)

    @abstractmethod
    def get_dag_status(self, dag, execution_time) -> Status:
        pass

    @abstractmethod
    def get_task_status(self, dag, task, execution_time) -> Status:
        pass

    @abstractmethod
    def set_dag_status(self, dag, execution_time, status) -> bool:
        pass

    @abstractmethod
    def set_task_status(self, dag, task, execution_time, status) -> bool:
        pass


class StatefulDAGMixin:
    @classmethod
    def _get_state_plugin(cls, parameters):
        state_parameters = None
        plugin = None

        if hasattr(parameters, 'dag_state') and parameters.dag_state:
            state_parameters = json.loads(parameters.dag_state)
        elif hasattr(parameters, 'get'):
            state_parameters = json.loads(parameters.get("DAG_STATE", "{}"))

        plugin_class = import_plugin(state_parameters["CLASS"])

        if plugin_class:
            plugin = plugin_class(state_parameters)

        return plugin
