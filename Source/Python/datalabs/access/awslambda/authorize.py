""" API endpoint-specific Lambda function Task wrapper. """
import os

from datalabs.access.task.authorize import AuthorizerParameters, AuthorizerTaskException
from datalabs.awslambda import TaskWrapper


class AuthorizerLambdaTaskWrapper(TaskWrapper):
    def _get_task_parameters(self):
        token = self._parameters.get('authorizationToken').strip()

        if not token.startswith('Bearer '):
            raise AuthorizerTaskException('Invalid bearer token: "{token}"')

        return AuthorizerParameters(
            token=token.split(' ')[1],
            endpoint=self._parameters.get('methodArn'),
            passport_url=os.environ.get('PASSPORT_URL')
        )

    def _handle_exception(self, exception: AuthorizerTaskException) -> (int, dict):
        return dict(message=exception.message)

    def _generate_response(self) -> (int, dict):
        return self._task.policy_document
