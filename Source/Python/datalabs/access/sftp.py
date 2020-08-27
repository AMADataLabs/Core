""" Secure FTP object """
from   dataclasses import dataclass
from   abc import abstractmethod
import os

import pandas
import pysftp

from   datalabs.access.credentials import Credentials
from   datalabs.access.datastore import Datastore


@dataclass
class Configuration:
    host: str='eft.ama-assn.org'

    @classmethod
    def load(cls, key: str):
        """ Load configuration from environment variables.
            Variables are of the form SFTP_<KEY>_<PARAMETER>='<value>'.
        """
        configuration = Configuration()
        configuration.host = cls._load_varaible(key, 'HOST') or configuration.host

        return configuration

    @classmethod
    def _load_varaible(cls, key, credential_type):
        name = f'SFTP_{key.upper()}_{credential_type.upper()}'

        return os.environ.get(name)


class ConfigurationException(Exception):
    pass


class SFTP(Datastore):
    def __init__(self, configuration: Configuration = None, credentials: Credentials = None, key: str = None):
        super().__init__(credentials, key or 'DEFAULT')

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

    def ls(self, path: str, filter: str=None):
        with self._connection.cd(path):
             files = self._connection.listdir()

        return self._filter_files(files, filter)

    @classmethod
    def _filter_files(cls, files: list, filter: str) -> list:
        filtered_files = files

        if filter and '*' in filter:
            filter_parts = filter.split('*')
            prefix = filter_parts[0]
            suffix = filter_parts[-1]
            filtered_files = [file for file in files if file.startswith(prefix) and file.endswith(suffix)]

        return filtered_files


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
