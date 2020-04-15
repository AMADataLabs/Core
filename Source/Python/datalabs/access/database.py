""" Generic database object intended to be subclassed by specific databases. """

import os

import pandas
import pyodbc

import datalabs.access.credentials as cred
from   datalabs.access.datastore import Datastore


class Database(Datastore):
    def __init__(self, credentials: cred.Credentials = None):
        super().__init__()
        self._database_name = self._load_database_name(self._key)

    def connect(self):
        self._connection = pyodbc.connect(
            f'DSN={self._database_name}; UID={self._credentials.username}; PWD={self._credentials.password}'
        )
        self._connection.execute('SET ISOLATION TO DIRTY READ;')

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
