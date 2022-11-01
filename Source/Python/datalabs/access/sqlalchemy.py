""" Generic database object intended to be subclassed by specific databases. """
from   dataclasses import dataclass

import pandas
import sqlalchemy
from   sqlalchemy.orm import sessionmaker

from   datalabs.access.datastore import Datastore
from   datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class DatabaseParameters:
    backend: str
    host: str
    port: str
    username: str
    password: str
    name: str = None


class Database(Datastore):
    @property
    def url(self):
        url = None
        credentials = ''
        port = ''
        name = ''

        if self._parameters.username and self._parameters.password:
            credentials = f'{self._parameters.username}:{self._parameters.password}@'

        if self._parameters.port:
            port = f':{self._parameters.port}'

        if self._parameters.name:
            name = f'/{self._parameters.name}'


        url = f"{self._parameters.backend}://{credentials}{self._parameters.host or ''}{port}{name}"

        return url

    def connect(self):
        LOGGER.info("Database connection URL: %s", self.url)
        engine = sqlalchemy.create_engine(self.url, echo=True)
        Session = sessionmaker(bind=engine)  # pylint: disable=invalid-name

        self._connection = Session().connection().connection

    def read(self, sql: str, **kwargs):
        return pandas.read_sql(sql, self._connection, **kwargs)

    def execute(self, sql: str, **kwargs):
        return self._connection.execute(sql, **kwargs)
