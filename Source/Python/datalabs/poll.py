""" Release endpoint classes. """
import json
import logging

from   abc import abstractmethod

from   datalabs.task import Task


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=assignment-from-no-return, inconsistent-return-statements, f-string-without-interpolation
class ExternalConditionPollingTask(Task):
    def run(self):
        request_parameters = [
            json.loads(self._data[0].decode())["request_id"],
            json.loads(self._data[0].decode())["results_filename"]
        ]

        if not self._is_ready(request_parameters)[0]:
            raise TaskNotReady(f'Task waited for emails validation')

        return [json.dumps(self._create_results_parameters(request_parameters)).encode()]

    @classmethod
    def _create_results_parameters(cls, request_parameters):
        return dict(request_id=request_parameters[0], results_filename=request_parameters[1])

    @abstractmethod
    def _is_ready(self, request_parameters):
        pass


class TaskNotReady(Exception):
    pass
