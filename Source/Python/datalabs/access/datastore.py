""" Generic database object intended to be subclassed by specific databases. """
from abc import ABC, abstractmethod
import logging

from   datalabs.parameter import ParameterValidatorMixin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class Datastore(ParameterValidatorMixin, ABC):
    PARAMETER_CLASS = None

    def __init__(self, parameters: dict):
        self._parameters = parameters
        self._connection = None
        self._log_parameters(parameters)

        if self.PARAMETER_CLASS:
            self._parameters = self._get_validated_parameters(parameters)

    @property
    def connection(self):
        return self._connection

    @classmethod
    def _log_parameters(cls, parameters):
        if hasattr(parameters, "__dataclass_fields__"):
            parameters = {key:getattr(parameters, key) for key in parameters.__dataclass_fields__.keys()}

        LOGGER.info('%s parameters: %s', cls.__name__, parameters)

    def __enter__(self):
        self.connect()

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    @abstractmethod
    def connect(self):
        # Setup self._connection
        pass

    def close(self):
        self._connection.close()

        self._connection = None
