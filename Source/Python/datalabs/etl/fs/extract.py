""" Local file system extractors """
from   glob import glob
import os

from   datalabs.etl.extract import FileExtractorTask
from   datalabs.etl.task import ETLException


class LocalFileExtractorTask(FileExtractorTask):
    def _get_files(self):
        base_path = self._parameters['BASE_PATH']

        files = [os.path.join(base_path, file) for file in self._parameters['FILES'].split(',')]

        return files

    def _get_client(self):
        class DummyFSClient:
            def __enter__(self):
                pass

            def __exit__(self, *args, **kwargs):
                pass

        return DummyFSClient()

    def _resolve_wildcard(self, file):
        files = glob(file)

        if len(files) == 0:
            raise FileNotFoundError(f"Unable to find file '{file}'")

        return files

    def _extract_file(self, file):
        file_path = file
        data = None

        try:
            with open(file_path, 'rb') as file:
                data = file.read()
        except Exception as exception:
            raise ETLException(f"Unable to read file '{file_path}'") from exception

        return data


class LocalUnicodeTextFileExtractorTask(LocalFileExtractorTask):
    @classmethod
    def _decode_data(cls, data):
        return data.decode('utf-8', errors='replace')


class LocalWindowsTextFileExtractorTask(LocalFileExtractorTask):
    @classmethod
    def _decode_data(cls, data):
        return data.decode('cp1252', errors='backslashreplace')
