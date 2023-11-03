""" API endpoint task classes. """
import json
import urllib
import logging

import urllib3

from datalabs.task import Task, TaskException, TaskWrapper

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

HTTP = urllib3.PoolManager()


class APIEndpointException(TaskException):
    def __init__(self, message, status_code=None):
        super().__init__(message)

        self._status_code = status_code or 400  # Invalid request

    @property
    def status_code(self):
        return self._status_code


class InvalidRequest(APIEndpointException):
    pass


class Unauthorized(APIEndpointException):
    def __init__(self, message):
        super().__init__(message, 401)


class ResourceNotFound(APIEndpointException):
    def __init__(self, message):
        super().__init__(message, 404)


class InternalServerError(APIEndpointException):
    def __init__(self, message):
        super().__init__(message, 500)


class APIEndpointTask(Task):
    def __init__(self, parameters: dict, data: "list<bytes>" = None):
        super().__init__(parameters, data)
        self._status_code = 200
        self._response_body = {}
        self._headers = {}

    @property
    def status_code(self):
        return self._status_code

    @property
    def response_body(self):
        return self._response_body

    @property
    def headers(self):
        return self._headers


class APIEndpointTaskWrapper(TaskWrapper):
    # pylint: disable=abstract-method
    def _handle_success(self) -> (int, dict):
        return self.task.status_code, self.task.headers, self.task.response_body

    # pylint: disable=abstract-method
    def _handle_exception(self, exception: APIEndpointException) -> (int, dict):
        status_code = exception.status_code
        body = dict(message=exception.message)

        return status_code, {}, body

    @classmethod
    def _merge_parameters(cls, parameters, new_parameters):
        return parameters


class PassportAuthenticatingEndpointMixin:
    @classmethod
    def _get_passport_access_token(cls, parameters):
        LOGGER.info("Getting AMA access token for client.")

        token_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        token_fields = {
            "grant_type": "client_credentials",
            "client_id": parameters.client_id,
            "client_secret": parameters.client_secret
        }
        token_body = urllib.parse.urlencode(token_fields)

        token_response = cls._request_ama_token(cls, token_headers, token_body, parameters.token_url)

        if token_response.status != 200:
            raise InternalServerError(
                f'Internal Server error caused by: {token_response.data}, status: {token_response.status}'
            )

        token_json = json.loads(token_response.data)

        return token_json['access_token']

    # pylint: disable=unused-argument
    def _request_ama_token(self, token_headers, token_body, token_url):
        return HTTP.request(
            'POST',
            token_url,
            headers=token_headers,
            body=token_body
        )
