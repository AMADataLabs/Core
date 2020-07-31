""" Abstract task base class for use with AWS Lambda and other task-based systems. """
from abc import ABC, abstractmethod
import logging

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class Task(ABC):
    def __init__(self, parameters):
        self._parameters = parameters

        LOGGER.debug('%s parameters: %s', self.__class__.__name__, self._parameters)

    @abstractmethod
    def run(self):
        pass


class TaskException(BaseException):
    @property
    def message(self):
        return self.args[0]  # pylint: disable=unsubscriptable-object
