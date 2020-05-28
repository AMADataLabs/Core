""" Generic database object intended to be subclassed by specific databases. """
from   dataclasses import dataclass
from   abc import abstractmethod
import os

import pandas

from   datalabs.access.credentials import Credentials
from   datalabs.access.datastore import Datastore


@dataclass
class Configuration:
    backend: str = None
    host: str = None
    name: str

    @classmethod
    def load(cls, key: str):
        """ Load configuration from environment variables.
            Variables are of the form DATABASE_<KEY>_BACKEND='<backend>',
            DATABASE_<KEY>_HOST='<host>', and DATABASE_<KEY>_NAME='<name>'.
        """
        backend = cls._load_credentials_variable(key, 'BACKEND')
        host = cls._load_credentials_variable(key, 'HOST')
        name = cls._load_credentials_variable(key, 'NAME')

        return Credentials(username=username, password=password)

    @classmethod
    def _load_credentials_variable(cls, key, credential_type):
        name = f'DATABASE_{key.upper()}_{credential_type.upper()}'
        value = os.environ.get(name)

        if value is None:
            raise ConfigurationException(f'Unable to load environment variable {name}.')

        return value


class ConfigurationException(Exception):
    pass


class Database(Datastore):
    def __init__(self, configuration: Configuration, credentials: Credentials):
        super().__init__(credentials)
        self._configuration = configuration
        self._database_name = self._load_database_name(self._key)

    @property
    def url(self):
        return "{}://{}:{}@{}/{}".format(
            self._configuration.backend,
            self._credentials.username,
            self._credentials.password,
            self._configuration.host,
            self._configuration.name,
        )

    @abstractmethod
    def connect(self):
        pass

    def read(self, sql: str, **kwargs):
        return pandas.read_sql(sql, self._connection, **kwargs)

    def execute(self, sql: str, **kwargs):
        return self._connection.execute(sql, **kwargs)

    @classmethod
    def _load_database_name(cls, key: str):
        database_name_variable = f'DATABASE_{key}_NAME'
        database_name = os.environ.get(database_name_variable)

        if database_name is None:
            raise ValueError(f'Missing or blank database name variable {database_name_variable}.')

        return database_name
