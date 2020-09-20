""" Base Lambda function Task wrapper class. """
from   abc import ABC, abstractmethod
import json

import datalabs.task as task


class TaskWrapper(task.TaskWrapper, ABC):
    @abstractmethod
    def _generate_response(self, task) -> (int, dict):
        pass

    @abstractmethod
    def _handle_exception(self, exception: Exception) -> (int, dict):
        pass
