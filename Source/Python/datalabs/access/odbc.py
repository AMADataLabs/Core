""" Generic database object intended to be subclassed by specific databases. """
import pyodbc

from   datalabs.access.database import Database


class ODBCDatabase(Database):
    def connect(self):
        self._connection = pyodbc.connect(
            f'DSN={self._database_name}; UID={self._credentials.username}; PWD={self._credentials.password}'
        )
        self._connection.execute('SET ISOLATION TO DIRTY READ;')
