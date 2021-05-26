""" Generic database object intended to be subclassed by specific databases. """
from   dataclasses import dataclass
from   abc import abstractmethod
import os

import pandas

from   datalabs.access.credentials import Credentials
from   datalabs.access.datastore import Datastore


@dataclass
class Configuration:
    name: str
    backend: str = None
    host: str = None
    port: str = None

    @classmethod
    def load(cls, key: str):
        """ Load configuration from environment variables.
            Variables are of the form DATABASE_<KEY>_BACKEND='<backend>',
            DATABASE_<KEY>_HOST='<host>', and DATABASE_<KEY>_NAME='<name>'.
        """
        name = cls._load_varaible(key, 'NAME')
        backend = cls._load_varaible(key, 'BACKEND')
        host = cls._load_varaible(key, 'HOST')
        port = cls._load_varaible(key, 'PORT')

        return Configuration(name, backend, host, port)

    @classmethod
    def _load_varaible(cls, key, credential_type):
        name = f'DATABASE_{key.upper()}_{credential_type.upper()}'
        value = os.environ.get(name)

        if value is None:
            raise ConfigurationException(f'Unable to load environment variable {name}.')

        return value


class ConfigurationException(Exception):
    pass


class Database(Datastore):
    def __init__(self, configuration: Configuration = None, credentials: Credentials = None, key: str = None):
        super().__init__(credentials, key)

        self._configuration = self._load_or_verify_configuration(configuration, self._key)

    @property
    def url(self):
        url = None
        credentials = ''
        port = ''
        name = ''

        if self._credentials.username and self._credentials.password:
            credentials = f'{self._credentials.username}:{self._credentials.password}@'

        if self._configuration.port:
            port = f':{self._configuration.port}'

        if self._configuration.name:
            name = f'/{self._configuration.name}'


        url = "{}://{}{}{}{}".format(
            self._configuration.backend,
            credentials,
            self._configuration.host or '',
            port,
            name,
        )

        return url

    @abstractmethod
    def connect(self):
        return self._connection

    def read(self, sql: str, **kwargs):
        return pandas.read_sql(sql, self._connection.connection(), **kwargs)

    def execute(self, sql: str, **kwargs):
        return self._connection.execute(sql, **kwargs)

    @classmethod
    def _load_or_verify_configuration(cls, configuration: Configuration, key: str):
        if configuration is None:
            configuration = Configuration.load(key)
        elif not hasattr(configuration, 'name') or \
             not hasattr(configuration, 'backend') or \
             not  hasattr(configuration, 'host'):
            raise ValueError('Invalid configuration object.')

        return configuration

    @classmethod
    def from_parameters(cls, parameters, prefix=None):
        if not prefix:
            prefix = ""

        prefix_lc = prefix.lower()

        config = Configuration(
            name=parameters.get(f'{prefix_lc}name') or parameters.get(f'{prefix}NAME'),
            backend=parameters.get(f'{prefix_lc}backend') or parameters.get(f'{prefix}BACKEND'),
            host=parameters.get(f'{prefix_lc}host') or parameters.get(f'{prefix}HOST'),
            port=parameters.get(f'{prefix_lc}port') or parameters.get(f'{prefix}PORT')
        )
        credentials = Credentials(
            username=parameters.get(f'{prefix_lc}username') or parameters.get(f'{prefix}USERNAME'),
            password=parameters.get(f'{prefix_lc}password') or parameters.get(f'{prefix}PASSWORD')
        )

        return cls(config, credentials)
