""" Secure FTP object """
from dataclasses import dataclass
import logging
import os
import re

import pandas
import pysftp

from   datalabs.access.datastore import Datastore
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class SFTPParameters:
    username: str
    password: str
    host: str='eft.ama-assn.org'


class SFTP(Datastore):
    PARAMETER_CLASS = SFTPParameters

    def connect(self):
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None

        self._connection = pysftp.Connection(
            self._parameters.host,
            username=self._parameters.username,
            password=self._parameters.password,
            cnopts=cnopts
        )

    # pylint: disable=redefined-builtin
    def list(self, path: str, filter: str = None, recurse: bool = False):
        files = []

        def file_callback(file):
            files.append(re.sub(r"^\./", "", file))

        # pylint: disable=unused-argument
        def directory_callback(directory):
            pass

        # pylint: disable=unused-argument
        def unknown_callback(file):
            pass

        with self._connection.cd(path):
            self._connection.walktree(
                './',
                file_callback,
                directory_callback,
                unknown_callback,
                recurse=recurse
            )

        return self._filter_files(files, filter)

    def list_directory(self, path: str, filter: str = None, recurse: bool = False):
        files = []

        # pylint: disable=unused-argument
        def file_callback(file):
            pass

        def directory_callback(directory):
            files.append(directory)

        # pylint: disable=unused-argument
        def unknown_callback(file):
            pass

        with self._connection.cd(path):
            self._connection.walktree(
                './',
                file_callback,
                directory_callback,
                unknown_callback,
                recurse=recurse
            )

        return self._filter_files(files, filter)

    def get(self, path: str, file):
        base_path = os.path.dirname(path)
        filename = os.path.basename(path)
        LOGGER.debug('Getting file %s', '/'.join((base_path, filename)))

        with self._connection.cd(base_path):
            self._connection.getfo(filename, file, callback=self._status_callback)

    def put(self, file, path: str):
        base_path = os.path.dirname(path)
        filename = os.path.basename(path)
        LOGGER.debug('Putting file %s', '/'.join((base_path, filename)))

        with self._connection.cd(base_path):
            self._connection.putfo(file, filename, callback=self._status_callback)

    @classmethod
    def _filter_files(cls, files: list, filter: str) -> list:
        filtered_files = files

        if filter and '*' in filter:
            filter_parts = filter.split('*')
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


class SFTPException(Exception):
    pass
