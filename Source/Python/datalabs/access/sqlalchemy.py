""" Generic database object intended to be subclassed by specific databases. """
from   dataclasses import dataclass
import logging

import sqlalchemy
from   sqlalchemy.orm import sessionmaker

import  datalabs.access.database as db
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class SQLAlchemyURLMixin:
    def _generate_connection_string(self):
        credentials = ''
        port = ''
        name = ''
        parameters = ''

        if self._parameters.username and self._parameters.password:
            credentials = f'{self._parameters.username}:{self._parameters.password}@'

        if self._parameters.port:
            port = f':{self._parameters.port}'

        if self._parameters.name:
            name = f'/{self._parameters.name}'

        if self._parameters.parameters is not None:
            parameters = f";{self._parameters.parameters}"

        return f"{self._parameters.backend}://{credentials}{self._parameters.host or ''}{port}{name}{parameters}"


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
    parameters: str = None


class Database(SQLAlchemyURLMixin, db.Database):
    PARAMETER_CLASS = DatabaseParameters

    def connect(self):
        LOGGER.info("Database connection URL: %s", self.connection_string)
        engine = sqlalchemy.create_engine(self.connection_string, echo=True)
        Session = sessionmaker(bind=engine)  # pylint: disable=invalid-name

        self._connection = Session().connection().connection
