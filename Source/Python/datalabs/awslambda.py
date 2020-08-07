""" Base Lambda function Task wrapper class. """
from   abc import ABC, abstractmethod
import json

import datalabs.task as task


class TaskWrapper(task.TaskWrapper, ABC):
    def run(self):
        status_code, headers, body = super().run()

        return {
            "statusCode": status_code,
            "headers": headers,
            "body": json.dumps(body),
            "isBase64Encoded": False,
        }

    @abstractmethod
    def _get_task_parameters(self):
        pass

    @abstractmethod
    def _generate_response(self, task) -> (int, dict):
        pass

    @abstractmethod
    def _handle_exception(self, exception: Exception) -> (int, dict):
        pass
