"""SFTP loader class"""
from   dataclasses import dataclass
import io
import os

from   datalabs.access import sftp
from   datalabs.etl.load import FileLoaderTask
from   datalabs.etl.task import ETLException, ExecutionTimeMixin
from   datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class SFTPFileLoaderParameters:
    base_path: str
    files: str
    host: str
    username: str
    password: str
    execution_time: str = None
    include_names: str = None


class SFTPFileLoaderTask(ExecutionTimeMixin, FileLoaderTask):
    PARAMETER_CLASS = SFTPFileLoaderParameters

    def _get_client(self):
        config = sftp.Configuration(
            host=self._parameters.host
        )
        credentials = sftp.Credentials(
            username=self._parameters.username,
            password=self._parameters.password
        )

        return sftp.SFTP(config, credentials)

    def _get_files(self):
        base_path = self._parameters.base_path
        file_paths = [os.path.join(base_path, file.strip()) for file in self._parameters.files.split(',')]

        return self._resolve_timestamps(file_paths)

    def _load_file(self, data, file):
        buffer = io.BytesIO(data)

        try:
            self._client.put(buffer, file)
        except Exception as exception:
            raise ETLException(f"Unable to write file '{file}'") from exception

# pylint: disable=too-many-ancestors
class SFTPWindowsTextFileLoaderTask(SFTPFileLoaderTask):
    @classmethod
    def _encode_data(cls, data):
        return data.decode().encode('cp1252', errors='backslashreplace')
