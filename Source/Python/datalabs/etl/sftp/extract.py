""" Local file system extractors """
from   dataclasses import dataclass
from   datetime import datetime
import io
import logging
import os

import datalabs.access.sftp as sftp
from   datalabs.etl.extract import FileExtractorTask, IncludeNamesMixin, ExecutionTimeMixin
from   datalabs.etl.task import ETLException
from   datalabs.task import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class SFTPFileExtractorParameters:
    base_path: str
    files: str
    host: str
    username: str
    password: str
    execution_time: str = None
    include_names: str = None
    data: object = None


class SFTPFileExtractorTask(IncludeNamesMixin, ExecutionTimeMixin, FileExtractorTask):
    PARAMETER_CLASS = SFTPFileExtractorParameters

    def _get_files(self):
        base_path = self._parameters.base_path

        return [os.path.join(base_path, file) for file in self._parameters.files.split(',')]

    def _get_client(self):
        config = sftp.Configuration(
            host=self._parameters.host
        )
        credentials = sftp.Credentials(
            username=self._parameters.username,
            password=self._parameters.password
        )

        return sftp.SFTP(config, credentials)

    def _resolve_wildcard(self, file):
        file_parts = file.split('*')
        base_path = os.path.dirname(file_parts[0])
        unresolved_file = f'{os.path.basename(file_parts[0])}*{file_parts[1]}'

        resolved_files = [os.path.join(base_path, file) for file in self._client.list(base_path, filter=unresolved_file)]

        if len(resolved_files) == 0:
            raise FileNotFoundError(f"Unable to find file '{file}'")

        return resolved_files

    # pylint: disable=arguments-differ
    def _extract_file(self, file):
        buffer = io.BytesIO()

        try:
            self._client.get(file, buffer)
        except Exception as exception:
            raise ETLException(f"Unable to read file '{file}'") from exception

        return bytes(buffer.getbuffer())


# pylint: disable=too-many-ancestors
class SFTPUnicodeTextFileExtractorTask(SFTPFileExtractorTask):
    @classmethod
    def _decode_data(cls, data):
        return data.decode('utf-8', errors='backslashreplace')


# pylint: disable=too-many-ancestors
class SFTPWindowsTextFileExtractorTask(SFTPFileExtractorTask):
    @classmethod
    def _decode_data(cls, data):
        return data.decode('cp1252', errors='backslashreplace')
