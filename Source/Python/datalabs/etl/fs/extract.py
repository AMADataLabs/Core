""" Local file system extractors """
from   glob import glob
import os

from   datalabs.etl.extract import FileExtractorTask
from   datalabs.etl.task import ETLException


class LocalFileExtractorTask(FileExtractorTask):
    def _extract(self):
        files = self._get_files()

        return self._extract_files(None, files)

    def _get_files(self):
        base_path = self._parameters.variables['BASEPATH']
        unresolved_files = [os.path.join(base_path, file) for file in self._parameters.variables['FILES'].split(',')]
        resolved_files = []

        for file in unresolved_files:
            files = self._resolve_filename(file)

            if isinstance(files, str):
                resolved_files.append(files)
            else:
                resolved_files += files

        return resolved_files

    #pylint: disable=arguments-differ
    def _extract_file(self, connection, file_path):
        data = None
        try:
            with open(file_path, 'rb') as file:
                data = file.read()
        except Exception as exception:
            raise ETLException(f"Unable to read file '{file_path}'") from exception

        return data

    @classmethod
    def _resolve_filename(cls, file_path):
        file_paths = glob(file_path)

        if len(file_paths) == 0:
            raise FileNotFoundError(f"Unable to find file '{file_path}'")

        return file_paths

    @classmethod
    def _decode_data(cls, data):
        return data


class LocalUnicodeTextFileExtractorTask(LocalFileExtractorTask):
    @classmethod
    def _decode_data(cls, data):
        return data.decode('utf-8', errors='replace')


class LocalWindowsTextFileExtractorTask(LocalFileExtractorTask):
    @classmethod
    def _decode_data(cls, data):
        return data.decode('cp1252', errors='backslashreplace')
