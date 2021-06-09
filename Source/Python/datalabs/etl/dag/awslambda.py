""" Task wrapper for DAG and DAG task Lambda functions. """
import json
import logging
import os

import datalabs.awslambda as awslambda
import datalabs.etl.task as task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class ETLTaskWrapper(task.ETLTaskParametersGetterMixin, awslambda.TaskWrapper):
    def _setup_environment(self):
        dynamodb_loader = DynamoDBEnvironmentLoader.from_environ()
        if dynamodb_loader is not None:
            dynamodb_loader.load()

        super()._setup_environment()

        self._resolve_parameter_store_environment_variables()

        self._resolve_secrets_manager_environment_variables()

    def _get_task_parameters(self):
        task_parameters = super()._get_task_parameters()

        if self._parameters and hasattr(self._parameters, 'items'):
            task_parameters = self._add_component_environment_variables_from_event(task_parameters, self._parameters)

        return task_parameters

    def _handle_success(self) -> (int, dict):
        return "Success"

    def _handle_exception(self, exception: task.ETLException) -> (int, dict):
        LOGGER.error('Handling ETL task exception: %s', exception)

        return f'Failed: {str(exception)}'

    @classmethod
    def _add_component_environment_variables_from_event(cls, task_parameters, event):
        environment_variables = {key.upper():str(value) for key, value in event.items()}
        component_variables = [
            task_parameters.extractor,
            task_parameters.transformer,
            task_parameters.loader
        ]

        for variables in component_variables:
            base_component_variables = environment_variables.copy()
            base_component_variables.update(variables)
            variables.clear()
            variables.update(base_component_variables)

        return task_parameters

    @classmethod
    def _resolve_secrets_manager_environment_variables(cls):
        super()._resolve_secrets_manager_environment_variables()

        cls._populate_database_parameters_from_secret()

    @classmethod
    def _populate_database_parameters_from_secret(cls):
        secrets = {
            key: value
            for name, secret in os.environ.items() if name.endswith('__DATABASE_SECRET')
            for key, value in cls._get_database_parameters_from_secret(name, secret).items()
        }

        for name, value in secrets.items():
            os.environ[name] = value

    @classmethod
    def _get_database_parameters_from_secret(cls, name, secret_string):
        prefix = name.replace('__DATABASE_SECRET', '__') + 'DATABASE_'
        secret = json.loads(secret_string)
        engine = secret.get('engine')
        variables = {
            prefix+'NAME': os.getenv(prefix+'NAME') or secret.get('dbname'),
            prefix+'PORT': os.getenv(prefix+'PORT') or str(secret.get('port')),
            prefix+'USERNAME': os.getenv(prefix+'USERNAME') or secret.get('username'),
            prefix+'PASSWORD': os.getenv(prefix+'PASSWORD') or secret.get('password')
        }

        if engine == 'postgres':
            variables[prefix+'BACKEND'] = os.getenv(prefix+'BACKEND') or 'postgresql+psycopg2'


        os.environ.pop(name)

        return variables
