""" Generic database object intended to be subclassed by specific databases. """
from   dataclasses import dataclass
import logging

import jaydebeapi
import pandas

import datalabs.access.database as db
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class DatabaseParameters:
    driver: str
    driver_type: str
    host: str
    username: str
    password: str
    port: str
    jar_path: str
    name: str = None
    parameters: str = None


class Database(db.Database):
    def connect(self):
        LOGGER.info("Database connection URL: %s", self.connection_string)

        self._connection = jaydebeapi.connect(
            self._parameters.driver,
            self.connection_string,
            [self._parameters.username, self._parameters.password],
            self._parameters.jar_path.split(',')
        )

    def read(self, sql: str, **kwargs):
        return pandas.read_sql(sql, self._connection, **kwargs)

    def execute(self, sql: str, **kwargs):
        cursor = self._connection.cursor()

        cursor.execute(sql, **kwargs)

        return cursor

    def _generate_connection_string(self):
        url = f"jdbc:{self._parameters.driver_type}://{self._parameters.host}:{self._parameters.port}"

        if self._parameters.name is not None:
            url += f"/{self._parameters.name}"

        if self._parameters.parameters is not None:
            url += f";{self._parameters.parameters}"

        return url
