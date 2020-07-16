""" API endpoint task classes. """
from abc import abstractmethod
from dataclasses import dataclass
from datalabs.task import Task, TaskException

from datalabs.access.credentials import Credentials
from datalabs.access.database import Configuration
from datalabs.access.orm import Database


@dataclass
class APIEndpointParameters:
    path: dict
    query: dict
    database: dict


class APIEndpointTask(Task):
    def __init__(self, parameters: APIEndpointParameters):
        super().__init__(parameters)
        self._status_code = 200
        self._response_body = dict()

    @property
    def status_code(self):
        return self._status_code

    @property
    def response_body(self):
        return self._response_body

    def run(self):
        with self._get_database() as database:
            self._run(database.session)  # pylint: disable=no-member

    @abstractmethod
    def _run(self, session):
        pass


    def _get_database(self):
        config = Configuration(
            name=self._parameters.database['name'],
            backend=self._parameters.database['backend'],
            host=self._parameters.database['host']
        )
        credentials = Credentials(
            username=self._parameters.database['username'],
            password=self._parameters.database['password']
        )

        return Database(config, credentials)


class APIEndpointException(TaskException):
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
