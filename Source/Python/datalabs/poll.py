""" Release endpoint classes. """
import logging

from   datalabs.task import TaskWrapper


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class TaskNotReady(Exception):
    pass


# pylint: disable=assignment-from-no-return, inconsistent-return-statements
class ExternalConditionPollingTask(TaskWrapper):

    def run(self):
        try:
            pull_emails = self._is_ready()

            if not pull_emails:
                raise ValueError('Task waited for emails validation')
            response = self._handle_success()

        except Exception as exception:  # pylint: disable=broad-except
            LOGGER.exception('Unable to run task.')
            response = self._handle_exception(exception)

            return response

    def _is_ready(self):
        pass
