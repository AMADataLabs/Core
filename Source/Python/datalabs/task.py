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


class TaskWrapper(ABC):
    def __init__(self, task_class, parameters=None):
        self._task_class = task_class
        self._parameters = parameters

    def run(self):
        task_parameters = self._get_task_parameters()
        task = self._task_class(task_parameters)

        try:
            task.run()

            response = self._generate_response(task)
        except TaskException as exception:
            response = self._handle_exception(exception)

        return response

    @abstractmethod
    def _get_task_parameters(self):
        pass

    @abstractmethod
    def _generate_response(self, task) -> (int, dict):
        pass

    @abstractmethod
    def _handle_exception(self, exception: Exception) -> (int, dict):
        pass
