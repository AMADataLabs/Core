""" Release endpoint classes. """
from   abc import abstractmethod
import json
import logging

from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=f-string-without-interpolation
class ExternalConditionPollingTask(Task):
    def __init__(self, parameters: dict, data: "list<bytes>"=None):
        super().__init__(parameters, data)
        self._request_parameters = None

    def run(self):
        self._request_parameters = json.loads(self._data[0])

        if not self._is_ready():
            raise TaskNotReady(f'Task waited for emails validation')

        return [json.dumps(self._create_results_parameters()).encode()]

    @abstractmethod
    def _is_ready(self):
        pass

    def _create_results_parameters(self):
        return self._request_parameters


class TaskNotReady(Exception):
    pass
