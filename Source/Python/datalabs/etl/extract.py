""" Extractor base class """
from   abc import ABC, abstractmethod
from   datetime import datetime
import pickle

from   datalabs.etl.task import ETLComponentTask, ETLException


class ExtractorTask(ETLComponentTask, ABC):
    def run(self):
        self._data = self._extract()

    @abstractmethod
    def _extract(self) -> "Extracted Data":
        pass


class IncludeNamesMixin:
    @property
    def include_names(self):
        include_names = False

        if hasattr(self._parameters, 'include_names') and self._parameters.include_names:
            include_names = self._parameters.include_names.upper() == 'TRUE'
        elif hasattr(self._parameters, 'get'):
            include_names = self._parameters.get('INCLUDE_NAMES', 'false').upper() == 'TRUE'

        return include_names


class NothingExtractorTask(ExtractorTask):
    def _extract(self) -> "Extracted Data":
        return []


class FileExtractorTask(ExtractorTask, ABC):
    def __init__(self, parameters):
        super().__init__(parameters)

        self._client = None
        self._execution_time = self.execution_time

    @property
    def include_names(self):
        return False

    @property
    def execution_time(self):
        return datetime.utcnow()

    def _extract(self):
        # pylint: disable=not-context-manager
        with self._get_client() as client:
            self._client = client

            files = self._get_files()

            resolved_files = self._resolve_files(files)

            data = self._extract_files(resolved_files)

        self._client = None

        decoded_data = self._decode_dataset(data, resolved_files)

        if self.include_names:
            decoded_data = [pickle.dumps(list(zip(resolved_files, decoded_data)))]

        return decoded_data

    @abstractmethod
    def _get_client(self) -> 'Context Manager':
        return None

    @abstractmethod
    def _get_files(self) -> list:
        return None

    def _resolve_files(self, files):
        timestamped_files = self._resolve_timestamps(files)

        expanded_files = self._resolve_wildcards(timestamped_files)

        return expanded_files

    def _extract_files(self, files):
        data = [self._extract_file(file) for file in files]

        return data

    def _decode_dataset(self, dataset, files):
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

    def _resolve_timestamps(self, files):
        return [datetime.strftime(self._execution_time, file) for file in files]

    @abstractmethod
    def _extract_file(self, file):
        return []

    @classmethod
    def _decode_data(cls, data):
        return data

    @abstractmethod
    def _resolve_wildcard(self, file):
        return None
