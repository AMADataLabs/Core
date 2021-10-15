""" API endpoint-specific Lambda function Task wrapper. """
import json
import os

import datalabs.access.api.task as api
from   datalabs.awslambda import TaskWrapper


class APIEndpointTaskWrapper(api.APIEndpointParametersGetterMixin, TaskWrapper):
    def _get_task_parameters(self):
        self._parameters['query'] = self._parameters.get('queryStringParameters') or dict()
        self._parameters['query'].update(self._parameters.get('multiValueQueryStringParameters') or dict())
        self._parameters['path'] = self._parameters.get('pathParameters') or dict()

        return super()._get_task_parameters()

    def _handle_success(self) -> (int, dict):
        return {
            "statusCode": self.task.status_code,
            "headers": self.task.headers,
            "body": json.dumps(self.task.response_body),
            "isBase64Encoded": False,
        }

    def _handle_exception(self, exception: api.APIEndpointException) -> (int, dict):
        status_code = None
        message = None

        if hasattr(exception, 'status_code'):
            status_code = exception.status_code
        else:
            status_code = 500

        if hasattr(exception, 'message'):
            message = json.dumps(dict(message=exception.message))
        else:
            message = str(exception)

        return {
            "statusCode": status_code,
            "headers": dict(),
            "body": message,
            "isBase64Encoded": False,
        }

    @classmethod
    def _merge_parameters(cls, parameters, new_parameters):
        return parameters

    @classmethod
    def _resolve_secrets_manager_environment_variables(cls):
        super()._resolve_secrets_manager_environment_variables()

        if 'DATABASE_SECRET' in os.environ:
            cls._populate_database_parameters_from_secret()

    @classmethod
    def _populate_database_parameters_from_secret(cls):
        secret = os.getenv('DATABASE_SECRET')

        for name, value in cls._get_database_parameters_from_secret('DATABASE_SECRET', secret).items():
            os.environ[name] = value

    @classmethod
    def _get_database_parameters_from_secret(cls, name, secret_string):
        secret = json.loads(secret_string)
        engine = secret.get('engine')
        variables = dict(
            DATABASE_NAME=os.getenv('DATABASE_NAME') or secret.get('dbname'),
            DATABASE_PORT=os.getenv('DATABASE_PORT') or str(secret.get('port')),
            DATABASE_USERNAME=os.getenv('DATABASE_USERNAME') or secret.get('username'),
            DATABASE_PASSWORD=os.getenv('DATABASE_PASSWORD') or secret.get('password')
        )

        if engine == 'postgres':
            variables['DATABASE_BACKEND'] = os.getenv('DATABASE_BACKEND') or 'postgresql+psycopg2'

        os.environ.pop(name)

        return variables
