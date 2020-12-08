""" REPLACE WITH DOCSTRING """
import json
import logging
import os

from   datalabs.access.parameter import ParameterStoreEnvironmentLoader
from   datalabs.access.secret import SecretsManagerEnvironmentLoader
import datalabs.awslambda as awslambda
import datalabs.etl.task as task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class ETLTaskWrapper(task.ETLTaskParametersGetterMixin, awslambda.TaskWrapper):
    def _get_task_parameters(self):
        self._resolve_parameter_store_environment_variables()

        self._resolve_secrets_manager_environment_variables()

        task_parameters = super()._get_task_parameters()

        if self._parameters and hasattr(self._parameters, 'items'):
            task_parameters = self._add_component_environment_variables_from_event(task_parameters, self._parameters)

        return task_parameters

    def _generate_response(self) -> (int, dict):
        return "Success"

    def _handle_exception(self, exception: task.ETLException) -> (int, dict):
        LOGGER.error('Handling ETL task exception: %s', exception)

        return f'Failed: {str(exception)}'

    @classmethod
    def _resolve_parameter_store_environment_variables(cls):
        parameter_loader = ParameterStoreEnvironmentLoader.from_environ()
        parameter_loader.load()

    @classmethod
    def _resolve_secrets_manager_environment_variables(cls):
        secrets_loader = SecretsManagerEnvironmentLoader.from_environ()
        secrets_loader.load()

        cls._populate_database_parameters_from_secret()

    @classmethod
    def _add_component_environment_variables_from_event(cls, task_parameters, event):
        environment_variables = {key.upper():str(value) for key, value in event.items()}
        component_variables = [
            task_parameters.extractor.variables,
            task_parameters.transformer.variables,
            task_parameters.loader.variables
        ]

        for variables in component_variables:
            variables.update(environment_variables)

        return task_parameters

    @classmethod
    def _populate_database_parameters_from_secret(cls):
        secrets = {
            key: value
            for name, secret in os.environ.items() if name.endswith('_DATABASESECRET')
            for key, value in cls._get_database_parameters_from_secret(name, secret).items()
        }

        for name, value in secrets.items():
            os.environ[name] = value

    @classmethod
    def _get_database_parameters_from_secret(cls, name, secret_string):
        prefix = name.replace('_DATABASESECRET', '_') + 'DATABASE_'
        secret = json.loads(secret_string)
        variables = {}

        variables[prefix+'USERNAME'] = secret.get('username')
        variables[prefix+'PASSWORD'] = secret.get('password')

        os.environ.pop(name)

        return variables
