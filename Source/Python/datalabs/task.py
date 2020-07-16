""" Abstract task base class for use with AWS Lambda and other task-based systems. """
from abc import ABC, abstractmethod


class Task(ABC):
    def __init__(self, parameters):
        self._parameters = parameters

    @abstractmethod
    def run(self):
        pass


class TaskException(BaseException):
    @property
    def message(self):
        return self.args[0]  # pylint: disable=unsubscriptable-object
