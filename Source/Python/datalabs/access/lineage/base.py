""" Lineage """
from   dataclasses import dataclass
from   abc import abstractmethod
import logging
import os

from   datalabs.access.credentials import Credentials
from   datalabs.access.datastore import Datastore

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class LineageLogger(Datastore):
    # pylint: disable=redefined-builtin
    @abstractmethod
    def log(self, parent_uri, child_uri, type=None):
        pass


@dataclass
class Configuration:
    host: str
    port: int = 8182

    @classmethod
    def load(cls, key: str):
        """ Load configuration from environment variables.
            Variables are of the form <KEY>_<PARAMETER>='<value>'.
        """
        configuration = Configuration(
            host=cls._load_varaible(key, 'HOST')
        )
        configuration.port = cls._load_varaible(key, 'PORT') or configuration.port

        return configuration

    @classmethod
    def _load_varaible(cls, key, credential_type):
        name = f'LINEAGE_{key.upper()}_{credential_type.upper()}'

        return os.environ.get(name)


class ConfigurationException(Exception):
    pass


class LineageException(Exception):
    pass


class LineageTaskMixin:
    @classmethod
    def _get_lineage(cls, parameters):
        config = Configuration(
            host=parameters['HOST'],
            port=parameters['PORT']
        )

        return cls(config)


def register_logger(key: str, logger_class: LineageLogger):
    LOGGERS[key.upper()] = logger_class


def get_logger(key: str, configuration: Configuration = None, credentials: Credentials = None):
    key = key.upper()

    if key not in LOGGERS:
        raise LineageException("No Lineage Logger registered for key '%s'." % key)

    return LOGGERS[key](configuration=configuration, credentials=credentials, key=key)


LOGGERS = {}
