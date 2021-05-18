""" DAG state classes. """
from   abc import ABC, abstractmethod
from   enum import Enum

from   datalabs.access.datastore import Datastore
from   datalabs.parameter import add_schema, ParameterValidatorMixin


class Status(Enum):
    Unknown = 'UNKNOWN'
    Pending = 'PENDING'
    Running = 'RUNNING'
    Finished = 'FINISHED'
    Failed = 'FAILED'


class State(ParameterValidatorMixin, Datastore, ABC):
    PARAMETER_CLASS = None

    def __init__(self, parameters: dict):
        self._parameters = parameters

        if self.PARAMETER_CLASS:
            self._parameters = self._get_validated_parameters(parameters)

    @abstractmethod
    def get_status(self, name, execution_time):
        pass

    @abstractmethod
    def set_status(self, name, execution_time, status):
        pass
