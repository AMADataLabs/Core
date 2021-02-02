""" API endpoint-specific Lambda function Task wrapper. """
import os

from   datalabs.access.authorize.task import AuthorizerParameters, AuthorizerTaskException
from   datalabs.access.parameter.aws import ParameterStoreEnvironmentLoader
from   datalabs.access.secret.aws import SecretsManagerEnvironmentLoader
from   datalabs.awslambda import TaskWrapper


class AuthorizerLambdaTaskWrapper(TaskWrapper):
    def _get_task_parameters(self):
        token = self._get_authorization_token()

        self._load_configuration()

        return self._authorize(token)

    def _get_authorization_token(self):
        token = self._parameters.get('authorizationToken').strip()

        if not token.startswith('Bearer '):
            raise AuthorizerTaskException('Invalid bearer token: "{token}"')

        return token

    @classmethod
    def _load_configuration(cls):
        parameter_loader = ParameterStoreEnvironmentLoader.from_environ()
        parameter_loader.load()

        secrets_loader = SecretsManagerEnvironmentLoader.from_environ()
        secrets_loader.load()

    def _authorize(self, token):
        return AuthorizerParameters(
            token=token.split(' ')[1],
            endpoint=self._parameters.get('methodArn'),
            passport_url=os.environ.get('PASSPORT_URL')
        )

    def _handle_exception(self, exception: AuthorizerTaskException) -> (int, dict):
        return dict(message=exception.message)

    def _generate_response(self) -> (int, dict):
        return self._task.policy_document
