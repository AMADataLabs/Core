from   datetime import datetime
import os

from   datalabs.etl.load import LoaderTask
from   datalabs.etl.task import ETLException


class LocalFileLoaderTask(LoaderTask):
    def _load(self):
        base_path = self._parameters.variables['BASEPATH']
        files = self._parameters.variables['FILES'].split(',')
        timestamped_files = self._resolve_timestamps(files)

        for file, data in zip(timestamped_files, self._parameters.data):
            self._load_file(base_path, file, data)

    @classmethod
    def _resolve_timestamps(cls, files):
        now = datetime.utcnow()

        return [datetime.strftime(now, file) for file in files]

    def _load_file(self, base_path, filename, data):
        file_path = os.path.join(base_path, filename)

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
