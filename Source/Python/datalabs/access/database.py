""" Generic database object intended to be subclassed by specific databases. """
from abc import abstractmethod
from   dataclasses import dataclass
import os

import pandas

from   datalabs.access.datastore import Datastore


class Database(Datastore):
    def __init__(self, parameters: dict):
        super().__init__(parameters)

        self._connection_string = self._generate_connection_string()

    @property
    def connection_string(self):
        return self._connection_string

    @abstractmethod
    def _generate_connection_string(self):
        pass

    def read(self, sql: str, **kwargs):
        return pandas.read_sql(sql, self._connection, **kwargs)

    def execute(self, sql: str, **kwargs):
        return self._connection.execute(sql, **kwargs)

    @classmethod
    def from_parameters(cls, parameters: dataclass) -> "Database":
        database_parameters = {
            key.replace("database_", ""):getattr(parameters, key)
            for key in parameters.__dataclass_fields__.keys()
            if key.startswith("database_")
        }

        return cls(database_parameters)

    @classmethod
    def from_environment(cls, key: str) -> "Database":
        database_parameters = {
            name.replace(f"DATABASE_{key}_", ""):value
            for name, value in os.environ.items()
            if name.startswith(f"DATABASE_{key}_")
        }

        return cls(database_parameters)
