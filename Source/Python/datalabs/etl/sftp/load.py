"""SFTP loader class"""
from   datetime import datetime
import io
import os

from   datalabs.access.sftp import SFTP, SFTPTaskMixin
from   datalabs.etl.load import LoaderTask
from   datalabs.etl.task import ETLException


class SFTPFileLoaderTask(LoaderTask, SFTPTaskMixin):
    def _load(self):
        file_paths = self._get_file_paths()

        with self._get_sftp(self._parameters.variables) as sftp:
            for file, data in zip(file_paths, self._parameters.data):
                self._load_file(sftp, data, file)

    def _get_file_paths(self):
        base_path = self._parameters.variables['BASEPATH']
        file_paths = [os.path.join(base_path, file) for file in self._parameters.variables['FILES'].split(',')]

        return self._resolve_timestamps(file_paths)

    def _load_file(self, sftp, data, file_path):
        data = self._encode_data(data)
        buffer = io.BytesIO(data)

        try:
            sftp.put(buffer, file_path)
        except Exception as exception:
            raise ETLException(f"Unable to write file '{file_path}'") from exception

    @classmethod
    def _encode_data(cls, data):
        return data

    @classmethod
    def _resolve_timestamps(cls, files):
        now = datetime.utcnow()

        return [datetime.strftime(now, file) for file in files]


class SFTPUnicodeTextFileLoaderTask(SFTPFileLoaderTask):
    @classmethod
    def _encode_data(cls, data):
        return data.encode('utf-8', errors='backslashreplace')


class SFTPWindowsTextFileLoaderTask(SFTPFileLoaderTask):
    @classmethod
    def _encode_data(cls, data):
        return data.encode('cp1252', errors='backslashreplace')
