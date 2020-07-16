""" REPLACE WITH DOCSTRING """
from abc import ABC, abstractmethod
from dataclasses import dataclass

from datalabs.access.credentials import Credentials
from datalabs.access.database import Configuration
from datalabs.access.orm import Database
from datalabs.task import Task, TaskException


class DatabaseTaskMixin(Task):
    def __init__(self, parameters):
        super().__init__(parameters)

        self._extractor = None
        self._transformer = None
        self._loader = None

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
