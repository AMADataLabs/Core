""" API endpoint-specific Lambda function Task wrapper. """
import json
import os

import datalabs.access.api.task as api
from   datalabs.access.parameter import ParameterStoreEnvironmentLoader
from   datalabs.access.secret import SecretsManagerEnvironmentLoader
from   datalabs.awslambda import TaskWrapper


class APIEndpointTaskWrapper(api.APIEndpointParametersGetterMixin, TaskWrapper):
    def _get_task_parameters(self):
        self._parameters['query'] = self._parameters.get('queryStringParameters') or dict()
        self._parameters['query'].update(self._parameters.get('multiValueQueryStringParameters') or dict())
        self._parameters['path'] = self._parameters.get('pathParameters') or dict()

        self._resolve_parameter_store_environment_variables()

        self._resolve_secrets_manager_environment_variables()

        return super()._get_task_parameters()

    def _generate_response(self) -> (int, dict):
        return {
            "statusCode": self._task.status_code,
            "headers": self._task.headers,
            "body": json.dumps(self._task.response_body),
            "isBase64Encoded": False,
        }

    def _handle_exception(self, exception: api.APIEndpointException) -> (int, dict):
        return {
            "statusCode": exception.status_code,
            "headers": dict(),
            "body": json.dumps(dict(message=exception.message)),
            "isBase64Encoded": False,
        }

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
    def _populate_database_parameters_from_secret(cls):
        secret = os.getenv('DATABASE_SECRET')

        for name, value in cls._get_database_parameters_from_secret('DATABASE_SECRET', secret).items():
            os.environ[name] = value

    @classmethod
    def _get_database_parameters_from_secret(cls, name, secret_string):
        secret = json.loads(secret_string)
        variables = dict(
            DATABASE_USERNAME=secret.get('username'),
            DATABASE_PASSWORD=secret.get('password')
        )

        os.environ.pop(name)

        return variables
