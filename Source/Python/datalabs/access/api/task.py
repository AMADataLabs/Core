""" API endpoint task classes. """
import logging

from   datalabs import task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class APIEndpointException(task.TaskException):
    def __init__(self, message, status_code=None):
        super().__init__(message)

        self._status_code = status_code or 400  # Invalid request

    @property
    def status_code(self):
        return self._status_code


class InvalidRequest(APIEndpointException):
    pass


class ResourceNotFound(APIEndpointException):
    def __init__(self, message):
        super().__init__(message, 404)


class InternalServerError(APIEndpointException):
    def __init__(self, message):
        super().__init__(message, 500)


class APIEndpointTask(task.Task):
    def __init__(self, parameters: dict):
        super().__init__(parameters)
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


class APIEndpointTaskWrapper(task.TaskWrapper):
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
