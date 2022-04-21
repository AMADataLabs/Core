""" Base Lambda function Task wrapper class. """
import logging

# pylint: disable=wrong-import-position
import datalabs.feature as feature
import datalabs.task as task


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class TaskWrapper(task.TaskWrapper):
    def _setup_environment(self):
        super()._setup_environment()

        if feature.enabled("PARAMETERS"):
            self._resolve_parameter_store_environment_variables()

        if feature.enabled("SECRETS"):
            self._resolve_secrets_manager_environment_variables()

    def _handle_success(self) -> (int, dict):
        return "Success"

    def _handle_exception(self, exception: Exception) -> (int, dict):
        LOGGER.error('Handling task exception: %s', exception)

        return f'Failed: {str(exception)}'

    @classmethod
    def _resolve_parameter_store_environment_variables(cls):
        from datalabs.access.parameter.aws import ParameterStoreEnvironmentLoader
        parameter_loader = ParameterStoreEnvironmentLoader.from_environ()
        parameter_loader.load()

    @classmethod
    def _resolve_secrets_manager_environment_variables(cls):
        from datalabs.access.secret.aws import SecretsManagerEnvironmentLoader
        secrets_loader = SecretsManagerEnvironmentLoader.from_environ()
        secrets_loader.load()
