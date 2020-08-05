""" Local file system extractors """
from   glob import glob
import os

from   datalabs.etl.extract import ExtractorTask
from   datalabs.etl.task import ETLException


class LocalFileExtractorTask(ExtractorTask):
    def _extract(self):
        files = self._get_files()

        return [(file, self._extract_file(file)) for file in files]

    def _get_files(self):
        base_path = self._parameters.variables['BASE_PATH']
        unresolved_files = [os.path.join((base_path, file)) for file in self._parameters.variables['FILES'].split(',')]
        resolved_files = []

        for file in unresolved_files:
            files = self._resolve_filename(file)

            if isinstance(files, str):
                resolved_files.append(files)
            else:
                resolved_files += files

        return resolved_files

    def _extract_file(self, file_path):
        data = None
        try:
            with open(file_path, 'rb') as file:
                data = file.read()
        except Exception as exception:
            raise ETLException(f"Unable to read file '{file_path}'": {exception}")

        return self._decode_data(data)

    def _resolve_filename(self, file_path):
        file_paths = glob(file_path)

        if len(file_paths) == 0:
            raise FileNotFoundError(f"Unable to find file '{file_path}'")

        return file_paths

    @classmethod
    def _decode_data(cls, data):
        return data


class WindowsTextExtractorTask(FileExtractorTask):
    @classmethod
    def _decode_data(cls, data):
        return data.decode('cp1252')
