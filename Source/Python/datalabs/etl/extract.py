""" Extractor base class """
from abc import ABC, abstractmethod

from datalabs.etl.task import ETLComponentTask


class ExtractorTask(ETLComponentTask, ABC):
    def run(self):
        self._data = self._extract()

    @abstractmethod
    def _extract(self) -> "Extracted Data":
        pass


class FileExtractorTask(ExtractorTask, ABC):
    def _extract_files(self, connection, files):
        include_filenames = self._parameters.variables.get('INCLUDENAMES')
        data = [self._extract_file(connection, file) for file in files]

        decoded_data = []
        for index,datum in enumerate(data):
            try:
                decoded_data.append(self._decode_data(datum))
            except Exception as exception:
                raise ETLException(f'Unable to decode {files[index]}') from exception

        if include_filenames and include_filenames.upper() == 'TRUE':
            decoded_data = list(zip(files, decoded_data))

        return decoded_data

    @abstractmethod
    def _extract_file(self, connection, file):
        return []

    @classmethod
    def _decode_data(cls, data):
        return data
