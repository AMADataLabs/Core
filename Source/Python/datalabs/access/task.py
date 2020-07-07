from abc import ABC, abstractmethod
from dataclasses import dataclass
from datalabs.task import Task

from datalabs.access.credentials import Credentials
from datalabs.access.orm import Database


@dataclass
class APIEndpointParameters:
    path: dict
    query: dict
    database: dict


class APIEndpointTask(Task):
    def __init__(self, parameters: APIEndpointParameters):
        self._parameters = parameters
        self._status_code = 200
        self._response_body = 'success'

    @property
    def status_code(self):
        return self._status_code

    @property
    def _response_body(self):
        return self._response_body

    def run(self):
        with self._get_database() as database:
            self._run(database.session)

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

        return database.Database(config, credentials)


class APIEndpointException(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message)

        self._status_code = status_code or 400  # Invalid request


class InvalidRequest(APIEndpointException):
    pass


class ResourceNotFound(APIEndpointException):
    def __init__(self, message):
        super().__init__(message, 404)
