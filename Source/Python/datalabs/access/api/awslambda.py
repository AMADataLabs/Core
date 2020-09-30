""" API endpoint-specific Lambda function Task wrapper. """
import json

import datalabs.access.api.task as api
from   datalabs.awslambda import TaskWrapper


class APIEndpointTaskWrapper(api.APIEndpointParametersGetterMixin, TaskWrapper):
    def _get_task_parameters(self):
        self._parameters['query'] = self._parameters.get('queryStringParameters') or dict()
        self._parameters['query'].update(self._parameters.get('multiValueQueryStringParameters') or dict())
        self._parameters['path'] = self._parameters.get('pathParameters') or dict()

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
