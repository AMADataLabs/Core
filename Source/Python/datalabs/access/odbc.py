""" Generic database object intended to be subclassed by specific databases. """
from   dataclasses import dataclass

# pylint: disable=import-error
import pyodbc

import datalabs.access.database as db
from   datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class DatabaseParameters:
    username: str
    password: str
    name: str = None


class Database(db.Database):
    PARAMETER_CLASS = DatabaseParameters

    def connect(self):
        self._connection = pyodbc.connect(self.connection_string)

        self._connection.execute('SET ISOLATION TO DIRTY READ;')

    def _generate_connection_string(self):
        return f'DSN={self._parameters.name}; UID={self._parameters.username}; PWD={self._parameters.password}'
