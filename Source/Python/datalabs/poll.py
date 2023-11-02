""" Release endpoint classes. """
from   abc import abstractmethod
import json
import logging

from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

# pylint: disable=assignment-from-no-return, inconsistent-return-statements, f-string-without-interpolation
class ExternalConditionPollingTask(Task):
    def run(self):
        request_parameters = json.loads(self._data[0])

        if not self._is_ready(request_parameters)[0]:
            raise TaskNotReady(f'Task waited for emails validation')

        return [json.dumps(self._create_results_parameters(request_parameters)).encode()]

    @classmethod
    def _create_results_parameters(cls, request_parameters):
        request_parameters_dict = {}

        if bool(request_parameters):
            request_parameters_dict = request_parameters

        return request_parameters_dict

    @abstractmethod
    def _is_ready(self, request_parameters):
        pass


class TaskNotReady(Exception):
    pass
