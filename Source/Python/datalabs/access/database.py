""" Generic database object intended to be subclassed by specific databases. """
from   abc import abstractmethod
import os

import pandas

from   datalabs.access.credentials import Credentials
from   datalabs.access.datastore import Datastore


class Database(Datastore):
    def __init__(self, credentials: Credentials = None):
        super().__init__(credentials)
        self._database_name = self._load_database_name(self._key)

    @abstractmethod
    def connect(self):
        pass

    def read(self, sql: str, **kwargs):
        return pandas.read_sql(sql, self._connection, **kwargs)

    def execute(self, sql: str, **kwargs):
        return self._connection.execute(sql, **kwargs)

    @classmethod
    def _load_database_name(cls, key: str):
        database_name_variable = f'DATABASE_NAME_{key}'
        database_name = os.environ.get(database_name_variable)

        if database_name is None:
            raise ValueError(f'Missing or blank database name variable {database_name_variable}.')

        return database_name
