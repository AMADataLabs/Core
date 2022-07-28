""" API endpoint-specific Lambda function Task wrapper. """
import json
import logging
import os

import datalabs.access.api.task as api
from   datalabs.awslambda import TaskWrapper

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class APIEndpointTaskWrapper(TaskWrapper):
    def _get_runtime_parameters(self, parameters):
        return dict(
            path = parameters.get('path', ""),
        )

    def _get_task_parameters(self):
        query_parameters = self._parameters.pop("queryStringParameters") or {}
        multivalue_query_parameters = self._parameters.pop("multiValueQueryStringParameters") or {}
        standard_parameters = dict(
            path=self._parameters.pop("pathParameters") or {},
            query={**query_parameters, **multivalue_query_parameters},
            authorization=self._extract_authorization_parameters(self._parameters)
        )
        task_specific_parameters = self._get_task_specific_parameters()

        return {**standard_parameters, **task_specific_parameters}

    def _handle_success(self) -> (int, dict):
        response = {
            "statusCode": self.task.status_code,
            "headers": self.task.headers,
            "body": json.dumps(self.task.response_body),
            "isBase64Encoded": False,
        }

        LOGGER.debug("API endpoint response: %s", response)

        return response

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

        LOGGER.exception("Handling API endpoint exception: %s", exception)

        return {
            "statusCode": status_code,
            "headers": {},
            "body": message,
            "isBase64Encoded": False,
        }

    @classmethod
    def _extract_authorization_parameters(cls, parameters):
        known_keys = ["customerNumber", "customerName", "principalId", "integrationLatency"]
        authorization_context = parameters["requestContext"]["authorizer"].copy()
        authorizations = {key:value for key, value in authorization_context.items() if key not in known_keys}

        return dict(
            user_id=authorization_context.get("customerNumber"),
            user_name=authorization_context.get("customerName"),
            authorizations=authorizations
        )

    # pylint: disable=no-self-use
    def _get_task_specific_parameters(self):
        ''' Get parameters specific to a particular endpoint. '''

        return dict(
            database_name=os.getenv('DATABASE_NAME'),
            database_backend=os.getenv('DATABASE_BACKEND'),
            database_host=os.getenv('DATABASE_HOST'),
            database_port=os.getenv('DATABASE_PORT'),
            database_username=os.getenv('DATABASE_USERNAME'),
            database_password=os.getenv('DATABASE_PASSWORD'),
            bucket_name=os.getenv('BUCKET_NAME'),
            bucket_base_path=os.getenv('BUCKET_BASE_PATH'),
            bucket_url_duration=os.getenv('BUCKET_URL_DURATION')
        )

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
            DATABASE_NAME=secret.get('dbname'),
            DATABASE_PORT=str(secret.get('port')),
            DATABASE_USERNAME=secret.get('username'),
            DATABASE_PASSWORD=secret.get('password')
        )

        if engine == 'postgres':
            variables['DATABASE_BACKEND'] = os.getenv('DATABASE_BACKEND') or 'postgresql+psycopg2'

        os.environ.pop(name)

        return variables
