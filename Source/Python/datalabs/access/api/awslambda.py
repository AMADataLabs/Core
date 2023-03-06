""" API endpoint-specific Lambda function Task wrapper. """
import json
import logging
import os
import re

import datalabs.access.api.task as api
from   datalabs.task import TaskWrapper
from   datalabs.plugin import import_plugin
from   datalabs.access.parameter.dynamodb import DynamoDBTaskParameterGetterMixin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class APIEndpointTaskWrapper(DynamoDBTaskParameterGetterMixin, TaskWrapper):
    def _get_runtime_parameters(self, parameters):
        api = os.environ['API_ID']
        path = parameters.get('path', "")
        route_parameters = self._get_dag_task_parameters_from_dynamodb(api, "ROUTE")
        task = self._get_task_id(api, path, route_parameters)
        task_parameters = self._get_dag_task_parameters_from_dynamodb(api, task)
        task_class = task_parameters.pop("TASK_CLASS")

        runtime_parameters = dict(
            TASK_CLASS=task_class,
            task_parameters=task_parameters
        )

        return runtime_parameters

    def _get_task_parameters(self):
        query_parameters = self._parameters.pop("queryStringParameters") or {}
        multivalue_query_parameters = self._parameters.pop("multiValueQueryStringParameters") or {}
        standard_parameters = dict(
            path=self._parameters.pop("pathParameters") or {},
            query={**query_parameters, **multivalue_query_parameters},
            payload=self._parameters.get("payload"),
            authorization=self._extract_authorization_parameters(self._parameters)
        )

        return {**standard_parameters, **self._runtime_parameters["task_parameters"]}

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

    def _get_task_resolver_class(self):
        task_resolver_class_name = os.environ.get('TASK_RESOLVER_CLASS', 'datalabs.task.RuntimeTaskResolver')
        task_resolver_class = import_plugin(task_resolver_class_name)

        if not hasattr(task_resolver_class, 'get_task_class'):
            raise TypeError(f'Task resolver {task_resolver_class_name} has no get_task_class method.')

        return task_resolver_class

    @classmethod
    def _get_task_id(cls, api_id, path, route_parameters):
        task_id = None

        for id, pattern in route_parameters.items():
            pattern = pattern.replace('*', '[^/]+')

            if re.match(pattern, path):
                task_id = id
                break
        LOGGER.info('Resolved path %s to implementation ID %s', path, str(task_id))

        return task_id

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
