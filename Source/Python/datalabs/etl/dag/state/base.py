""" ETL DAG state classes """
from   abc import ABC, abstractmethod
from   enum import Enum

from   datalabs.access.datastore import Datastore
from   datalabs.parameter import ParameterValidatorMixin


class Status(Enum):
    UNKNOWN = 'Unknown'
    PENDING = 'Pending'
    RUNNING = 'Running'
    FINISHED = 'Finished'
    FAILED = 'Failed'


class State(ParameterValidatorMixin, ABC):
    PARAMETER_CLASS = None

    # pylint: disable=super-init-not-called
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
