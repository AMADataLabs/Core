"""Local file system loader"""
from   datetime import datetime
import os

from   datalabs.etl.load import LoaderTask
from   datalabs.etl.task import ETLException


class LocalFileLoaderTask(LoaderTask):
    def _load(self):
        files = self._get_files()

        timestamped_files = self._resolve_timestamps(files)

        for file, data in zip(timestamped_files, self._parameters['data']):
            self._load_file(file, data)

    def _get_files(self):
        base_path = self._parameters['BASE_PATH']

        files = [os.path.join(base_path, file.strip()) for file in self._parameters['FILES'].split(',')]

        return files

    @classmethod
    def _resolve_timestamps(cls, files):
        now = datetime.utcnow()

        return [datetime.strftime(now, file) for file in files]

    def _load_file(self, file_path, data):
        data = self._encode_data(data)

        try:
            with open(file_path, 'wb') as file:
                file.write(data)
        except Exception as exception:
            raise ETLException(f"Unable to write file '{file_path}'") from exception

    @classmethod
    def _encode_data(cls, data):
        return data


class LocalUnicodeTextFileLoaderTask(LocalFileLoaderTask):
    @classmethod
    def _encode_data(cls, data):
        return data.encode('utf-8', errors='backslashreplace')


class LocalWindowsTextFileLoaderTask(LocalFileLoaderTask):
    @classmethod
    def _encode_data(cls, data):
        return data.encode('cp1252', errors='backslashreplace')
