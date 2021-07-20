""" API endpoint task classes. """
from   abc import abstractmethod
from   dataclasses import dataclass
import logging
import os

from   datalabs.access.orm import Database
import datalabs.task as task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@dataclass
class APIEndpointParameters:
    path: dict
    query: dict
    database: dict
    bucket: dict


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


class APIEndpointTask(task.Task, task.DatabaseTaskMixin):
    def __init__(self, parameters: APIEndpointParameters):
        super().__init__(parameters)
        self._status_code = 200
        self._response_body = dict()
        self._headers = dict()

    @property
    def status_code(self):
        return self._status_code

    @property
    def response_body(self):
        return self._response_body

    @property
    def headers(self):
        return self._headers

    def run(self):
        with Database.from_parameters(self._parameters.database) as database:
            self._run(database)  # pylint: disable=no-member

    @abstractmethod
    def _run(self, database):
        pass


# pylint: disable=abstract-method
class APIEndpointParametersGetterMixin(task.TaskWrapper):
    def _get_task_parameters(self):
        query_parameters = self._parameters.get('query') or dict()

        return APIEndpointParameters(
            path=self._parameters.get('path') or dict(),
            query=query_parameters,
            database=dict(
                name=os.getenv('DATABASE_NAME'),
                backend=os.getenv('DATABASE_BACKEND'),
                host=os.getenv('DATABASE_HOST'),
                port=os.getenv('DATABASE_PORT'),
                username=os.getenv('DATABASE_USERNAME'),
                password=os.getenv('DATABASE_PASSWORD')
            ),
            bucket=dict(
                name=os.getenv('BUCKET_NAME'),
                base_path=os.getenv('BUCKET_BASE_PATH'),
                url_duration=os.getenv('BUCKET_URL_DURATION'),
            )
        )


class APIEndpointTaskWrapper(APIEndpointParametersGetterMixin, task.TaskWrapper):
    # pylint: disable=abstract-method
    def _handle_success(self) -> (int, dict):
        return self.task.status_code, self.task.headers, self.task.response_body

    # pylint: disable=abstract-method
    def _handle_exception(self, exception: APIEndpointException) -> (int, dict):
        status_code = exception.status_code
        body = dict(message=exception.message)

        return status_code, dict(), body

    @classmethod
    def _merge_parameters(cls, parameters, new_parameters):
        return parameters
