""" Abstract task base class for use with AWS Lambda and other task-based systems. """
from abc import ABC, abstractmethod
import logging

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


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
        self._parameters = parameters or {}
        self._task = None

        if not hasattr(self._task_class, 'run'):
            raise TypeError('Task class does not have a "run" method.')

    def run(self):
        task_parameters = self._get_task_parameters()
        self._task = self._task_class(task_parameters)

        try:
            self._task.run()

            response = self._handle_success()
        except TaskException as exception:
            response = self._handle_exception(exception)

        return response

    def _get_task_parameters(self):
        return self._parameters

    @abstractmethod
    def _handle_success(self) -> (int, dict):
        pass

    @abstractmethod
    def _handle_exception(self, exception: Exception) -> (int, dict):
        pass
