""" Base Lambda function Task wrapper class. """
import logging

from   datalabs.access.parameter.aws import ParameterStoreEnvironmentLoader
from   datalabs.access.secret.aws import SecretsManagerEnvironmentLoader
import datalabs.task as task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class TaskWrapper(task.TaskWrapper):
    def _setup_environment(self):
        super()._setup_environment()

        self._resolve_parameter_store_environment_variables()

        self._resolve_secrets_manager_environment_variables()

    def _handle_success(self) -> (int, dict):
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
