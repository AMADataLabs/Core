""" Secure FTP object """
from   dataclasses import dataclass
import logging
import os
import pandas
import pysftp

from   datalabs.access.credentials import Credentials
from   datalabs.access.datastore import Datastore

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@dataclass
class Configuration:
    host: str = 'eft.ama-assn.org'

    @classmethod
    def load(cls, key: str):
        """ Load configuration from environment variables.
            Variables are of the form <KEY>_<PARAMETER>='<value>'.
        """
        configuration = Configuration()
        configuration.host = cls._load_varaible(key, 'HOST') or configuration.host

        return configuration

    @classmethod
    def _load_varaible(cls, key, credential_type):
        name = f'{key.upper()}_{credential_type.upper()}'

        return os.environ.get(name)


class ConfigurationException(Exception):
    pass


class SFTP(Datastore):
    def __init__(self, configuration: Configuration = None, credentials: Credentials = None, key: str = None):
        super().__init__(credentials, key)

        self._configuration = self._load_or_verify_configuration(configuration, self._key)

    def connect(self):
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None

        self._connection = pysftp.Connection(
            self._configuration.host,
            username=self._credentials.username,
            password=self._credentials.password,
            cnopts=cnopts
        )

    def ls_files(self, path: str, filtering: str = None):
        with self._connection.cd(path):
            files = self._connection.listdir()

        return self._filter_files(files, filtering)

    def get(self, path: str, file):
        base_path = os.path.dirname(path)
        filename = os.path.basename(path)

        with self._connection.cd(base_path):
            self._connection.getfo(filename, file, callback=self._status_callback)

    def put(self, file, path: str):
        base_path = os.path.dirname(path)
        filename = os.path.basename(path)

        with self._connection.cd(base_path):
            self._connection.putfo(file, filename, callback=self._status_callback)

    @classmethod
    def _filter_files(cls, files: list, filtering: str) -> list:
        filtered_files = files

        if filtering and '*' in filtering:
            filter_parts = filtering.split('*')
            prefix = filter_parts[0]
            suffix = filter_parts[-1]
            filtered_files = [file for file in files if file.startswith(prefix) and file.endswith(suffix)]

        return filtered_files

    @classmethod
    def _status_callback(cls, bytes_transfered, total_bytes):
        if total_bytes > 0:
            percent_transfered = round(bytes_transfered / total_bytes * 100)
            LOGGER.debug('Transfered %s bytes of %s (%d %%)', bytes_transfered, total_bytes, percent_transfered)


    def read(self, sql: str, **kwargs):
        return pandas.read_sql(sql, self._connection, **kwargs)

    @classmethod
    def _load_or_verify_configuration(cls, configuration: Configuration, key: str):
        if configuration is None:
            configuration = Configuration.load(key)
        elif not hasattr(configuration, 'host'):
            raise ValueError('Invalid configuration object.')

        return configuration


class SFTPException(Exception):
    pass


# pylint: disable=abstract-method
class SFTPTaskMixin:
    @classmethod
    def _get_sftp(cls, parameters):
        config = Configuration(
            host=parameters['HOST']
        )
        credentials = Credentials(
            username=parameters['USERNAME'],
            password=parameters['PASSWORD']
        )

        return SFTP(config, credentials)
