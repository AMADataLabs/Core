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
        self._parameters["headers"] = {key.lower():value for key, value in self._parameters["headers"].items()}
        token = self._get_authorization_token()
        LOGGER.info('Bearer token: %s', token)

        return self._get_authorization_parameters(token)

    def _get_authorization_token(self):
        token = self._parameters["headers"].get("authorization").strip()

        if not token.startswith('Bearer '):
            raise AuthorizerTaskException('Invalid bearer token: "{token}"')

        return token

    def _get_authorization_parameters(self, token):
        LOGGER.debug("Authorization Lambda event:\n%s", self._parameters)
        return AuthorizerParameters(
            token=token.split(' ')[1],
            endpoint=self._parameters.get('methodArn'),
            passport_url=os.environ.get('PASSPORT_URL'),
            customer=self._parameters["headers"].get("x-customer-nbr"),
        )

    def _handle_exception(self, exception: AuthorizerTaskException) -> (int, dict):
        LOGGER.exception('An error occurred during authorization')
        return dict(message=exception.message)

    def _handle_success(self) -> (int, dict):
        LOGGER.info('Authorization:\n%s', self.task.authorization)
        return self.task.authorization

    # pylint: disable=unused-argument
    @classmethod
    def _extract_cache_parameters(cls, task_parameters):
        pass

    def _get_task_input_data(self):
        pass

    # pylint: disable=unused-argument
    def _put_task_output_data(self, data):
        pass
