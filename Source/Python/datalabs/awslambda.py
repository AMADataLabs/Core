""" Base Lambda function Task wrapper class. """
from   abc import ABC
import logging

from   datalabs.access.parameter import ParameterStoreEnvironmentLoader
from   datalabs.access.secret import SecretsManagerEnvironmentLoader
import datalabs.task as task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class TaskWrapper(task.TaskWrapper, ABC):
    def _get_task_parameters(self):
        ''' Resolve ARNs in environment variables that point Parameter Store and
        Secrets Manager resources. Overrides of this method should super() it
        and actually return parameters.'''
        self._resolve_parameter_store_environment_variables()

        self._resolve_secrets_manager_environment_variables()


    def _generate_response(self) -> (int, dict):
        return "Success"

    def _handle_exception(self, exception: Exception) -> (int, dict):
        LOGGER.error('Handling task exception: %s', exception)

        return f'Failed: {str(exception)}'

    @classmethod
    def _resolve_parameter_store_environment_variables(cls):
        parameter_loader = ParameterStoreEnvironmentLoader.from_environ()
        parameter_loader.load()

    @classmethod
    def _resolve_secrets_manager_environment_variables(cls):
        secrets_loader = SecretsManagerEnvironmentLoader.from_environ()
        secrets_loader.load()
