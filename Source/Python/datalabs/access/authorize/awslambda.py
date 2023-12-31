""" API endpoint-specific Lambda function Task wrapper. """
import logging
import os
from typing import Any, Dict

from datalabs.access.authorize.task import AuthorizerTaskException
from datalabs.awslambda import TaskWrapper

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class AuthorizerLambdaTaskWrapper(TaskWrapper):
    def _get_task_parameters(self):
        self._parameters["headers"] = {key.lower(): value for key, value in self._parameters["headers"].items()}
        token = self._get_authorization_token()
        LOGGER.info("Bearer token: %s", token)

        return self._get_authorization_parameters(token)

    def _get_authorization_token(self):
        token = self._parameters["headers"].get("authorization").strip()

        if not token.startswith("Bearer "):
            raise AuthorizerTaskException('Invalid bearer token: "{token}"')

        return token

    def _get_authorization_parameters(self, token) -> dict:
        LOGGER.debug("Authorization Lambda event:\n%s", self._parameters)
        parameters = dict(
            token=token.split(" ")[1],
            endpoint=self._parameters.get("methodArn"),
            passport_url=os.environ.get("PASSPORT_URL"),
        )

        if "x-customer-nbr" in self._parameters["headers"]:
            parameters["customer"] = self._parameters["headers"]["x-customer-nbr"]

        return parameters

    def _handle_exception(self, exception: AuthorizerTaskException) -> Dict[str, Any]:
        LOGGER.exception("An error occurred during authorization")
        return dict(message=exception.message)

    def _handle_success(self) -> Dict[str, Any]:
        LOGGER.info("Authorization:\n%s", self.task.authorization)
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
