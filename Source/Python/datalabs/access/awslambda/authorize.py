""" API endpoint-specific Lambda function Task wrapper. """
import os

from datalabs.access.task.authorize import AuthorizerParameters, AuthorizerTaskException
from datalabs.awslambda import TaskWrapper


class AuthorizerLambdaTaskWrapper(TaskWrapper):
    def _get_task_parameters(self, event: dict):
        query_parameters = event.get('queryStringParameters') or dict()
        query_parameters.update(event.get('multiValueQueryStringParameters') or dict())

        return AuthorizerParameters(
            token=event.get('bearerToken') or None,
            # TODO: this needs to be configurable
            passport_url='https://amapassport-test.ama-assn.org/auth/entitlements/list/CPTAPI'
        )

    def _handle_exception(self, exception: AuthorizerTaskException) -> (int, dict):
        status_code = exception.status_code
        body = dict(message=exception.message)

        return status_code, dict(), body

    def _generate_response(self, task) -> (int, dict):
        return task.status_code, task.headers, task.response_body
