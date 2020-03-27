""" Generic database object intended to be subclassed by specific databases. """

import os

import pandas
import pyodbc

import datalabs.access.credentials as cred


class Database():
    def __init__(self, credentials: cred.Credentials = None):
        self._key = self.__class__.__name__.upper()
        self._credentials = self._load_credentials(credentials, self._key)
        self._database_name = self._load_database_name(self._key)
        self._connection = None

    def connect(self):
        self._connection = pyodbc.connect(
            f'DSN={self._database_name}; UID={self._credentials.username}; PWD={self._credentials.username}'
        )
        self._connection.execute('SET ISOLATION TO DIRTY READ;')

    def read(self, sql: str):
        return pandas.read_sql(sql, self._connection)

    def execute(self, sql: str):
        return self._connection.execute(sql)

    @classmethod
    def _load_credentials(cls, credentials: cred.Credentials, key: str):
        if credentials is None:
            credentials = cred.Credentials.load(key)
        elif not hasattr(credentials, 'username') or hasattr(credentials, 'password'):
            raise ValueError('Invalid credentials object.')

        return credentials

    @classmethod
    def _load_database_name(cls, key: str):
        database_name_variable = f'DATABASE_NAME_{key}'
        database_name = os.environ.get(database_name_variable)

        if database_name is None:
            raise ValueError(f'Missing or blank database name variable {database_name_variable}.')

        return database_name
