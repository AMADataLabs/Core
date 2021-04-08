""" API endpoint-specific Lambda function Task wrapper. """
import logging
import os

from   datalabs.access.authorize.task import AuthorizerParameters, AuthorizerTaskException
from   datalabs.awslambda import TaskWrapper

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class AuthorizerLambdaTaskWrapper(TaskWrapper):
    def _get_task_parameters(self):
        token = self._get_authorization_token()
        LOGGER.info('Bearer token: %s', token)

        return self._get_authorization_parameters(token)

    def _get_authorization_token(self):
        token = self._parameters.get('authorizationToken').strip()

        if not token.startswith('Bearer '):
            raise AuthorizerTaskException('Invalid bearer token: "{token}"')

        return token

    def _get_authorization_parameters(self, token):
        return AuthorizerParameters(
            token=token.split(' ')[1],
            endpoint=self._parameters.get('methodArn'),
            passport_url=os.environ.get('PASSPORT_URL')
        )

    def _handle_exception(self, exception: AuthorizerTaskException) -> (int, dict):
        LOGGER.exception('An error occurred during authorization:')
        return dict(message=exception.message)

    def _handle_success(self) -> (int, dict):
        LOGGER.info('Policy document:\n%s', self.task.policy_document)
        return self.task.policy_document
