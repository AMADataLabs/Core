""" Base Lambda function Task wrapper class. """
from   abc import ABC, abstractmethod
import json

from   datalabs.task import TaskException


class TaskWrapper(ABC):
    def __init__(self, task_class):
        self._task_class = task_class

    def run(self, event):
        status_code = 200
        body = None
        parameters = self._get_task_parameters(event)

        if self._task_class is None:
            raise KeyError('Task class is not set. Use/implement the wrap() method to set.')

        task = self._task_class(parameters)

        try:
            task.run()

            status_code, headers, body = self._generate_response(task)
        except TaskException as exception:
            status_code, headers, body = self._handle_exception(exception)

        return {
            "statusCode": status_code,
            "headers": headers,
            "body": json.dumps(body),
            "isBase64Encoded": False,
        }

    @abstractmethod
    def _get_task_parameters(self, event: dict):
        pass

    @abstractmethod
    def _generate_response(self, task) -> (int, dict):
        pass

    @abstractmethod
    def _handle_exception(self, exception: Exception) -> (int, dict):
        pass
