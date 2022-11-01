""" Generic database object intended to be subclassed by specific databases. """
from   dataclasses import dataclass

import jaydebeapi
import pandas

from   datalabs.access.datastore import Datastore
from   datalabs.parameter import add_schema


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


class Database(Datastore):
    @property
    def url(self):
        url = f"jdbc:{self._parameters.driver_type}://{self._parameters.host}:" \
              f"{self._parameters.port}"

        if self._parameters.name is not None:
            url += f"/{self._dparameters.name}"

        if self._parameters.parameters is not None:
            url += f";{self._parameters.parameters}"

        return url

    def connect(self):
        LOGGER.info("Database connection URL: %s", self.url)

        self._connection = jaydebeapi.connect(
            self._parameters.driver,
            url,
            [self._parameters.username, self._parameters.password],
            self._parameters.jar_path.split(',')
        )

    def read(self, sql: str, **kwargs):
        return pandas.read_sql(sql, self._connection, **kwargs)

    def execute(self, sql: str, **kwargs):
        return self._connection.execute(sql, **kwargs)
