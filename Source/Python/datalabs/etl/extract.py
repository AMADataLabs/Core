""" Extractor base class """
from   abc import ABC, abstractmethod
from   datetime import datetime

from   datalabs.etl.task import ETLComponentTask, ETLException


class ExtractorTask(ETLComponentTask, ABC):
    def run(self):
        self._data = self._extract()

    @abstractmethod
    def _extract(self) -> "Extracted Data":
        pass


class FileExtractorTask(ExtractorTask, ABC):
    def __init__(self, parameters):
        super().__init__(parameters)

        self._client = None
        self._include_names = False

        if hasattr(self._parameters, 'include_names') and self._parameters.include_names:
            self._include_names = self._parameters.include_names.upper() == 'TRUE'
        elif hasattr(self._parameters, 'get'):
            self._include_names = self._parameters.get('INCLUDE_NAMES', 'false').upper() == 'TRUE'

    def _extract(self):
        files = self._get_files()

        with self._get_client() as client:
            self._client = client

            resolved_files = self._resolve_files(files)

            data = self._extract_files(resolved_files)

        self._client = None

        decoded_data = self._decode_dataset(data)

        if self._include_names:
            decoded_data = list(zip(resolved_files, decoded_data))

        return decoded_data

    @abstractmethod
    def _get_files(self) -> list:
        return None

    def _resolve_files(self, files):
        expanded_files = self._resolve_wildcards(files)

        return self._resolve_timestamps(expanded_files)

    @abstractmethod
    def _get_client(self) -> 'Context Manager':
        return None

    def _extract_files(self, files):
        data = [self._extract_file(file) for file in files]

        return data

    def _decode_dataset(self, dataset):
        decoded_dataset = []

        for index, data in enumerate(dataset):
            try:
                decoded_dataset.append(self._decode_data(data))
            except Exception as exception:
                raise ETLException(f'Unable to decode {files[index]}') from exception

        return decoded_dataset

    def _resolve_wildcards(self, files):
        expanded_files = []

        for file in files:
            expanded_files.extend(self._resolve_wildcard(file))

        return expanded_files

    @classmethod
    def _resolve_timestamps(cls, files):
        now = datetime.utcnow()

        return [datetime.strftime(now, file) for file in files]

    @abstractmethod
    def _extract_file(self, file):
        return []

    @classmethod
    def _decode_data(cls, data):
        return data

    @abstractmethod
    def _resolve_wildcard(self, file):
        return None
