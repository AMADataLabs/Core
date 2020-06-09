""" Generic database object intended to be subclassed by specific databases. """
import os

import pyodbc

from   datalabs.access.database import Database


class ODBCDatabase(Database):
    def __init__(self):
        os.environ['DATABASE_AIMS_BACKEND'] = 'odbc'
        os.environ['DATABASE_AIMS_HOST'] = 'odbc'

        super().__init__()

    def connect(self):
        self._connection = pyodbc.connect(
            f'DSN={self._configuration.name}; UID={self._credentials.username}; PWD={self._credentials.password}'
        )
        self._connection.execute('SET ISOLATION TO DIRTY READ;')
