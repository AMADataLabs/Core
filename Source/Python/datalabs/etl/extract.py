""" Extractor base class """
from   abc import ABC, abstractmethod
from   datetime import datetime, timedelta
import json
import logging
import pickle

from   dateutil.parser import isoparse

from   datalabs.etl.task import ETLException, ExecutionTimeMixin
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class IncludeNamesMixin:
    @property
    def include_names(self):
        include_names = False

        if hasattr(self._parameters, 'include_names') and self._parameters.include_names:
            include_names = self._parameters.include_names.upper() == 'TRUE'
        elif hasattr(self._parameters, 'get'):
            include_names = self._parameters.get('INCLUDE_NAMES', 'false').upper() == 'TRUE'

        return include_names


class TargetOffsetMixin:
    def _get_target_datetime(self):
        target_offset = {}

        if hasattr(self._parameters, 'execution_offset') and self._parameters.execution_offset:
            target_offset = json.loads(self._parameters.execution_offset)

        elif hasattr(self._parameters, 'get') and self._parameters.get('EXECUTION_OFFSET'):
            target_offset = json.loads(self._parameters.get('EXECUTION_OFFSET'))

        return self.execution_time - timedelta(**target_offset)


class NothingExtractorTask(Task):
    def run(self) -> "Extracted Data":
        return []


class FileExtractorTask(ExecutionTimeMixin, Task, ABC):
    def __init__(self, parameters, data: "list<bytes>"=None):
        super().__init__(parameters, data)

        self._client = None

    @property
    def include_names(self):
        return False

    @property
    def execution_time(self):
        execution_time = datetime.utcnow().replace(second=0, microsecond=0, minute=0, hour=0)

        if hasattr(self._parameters, 'execution_time') and self._parameters.execution_time:
            execution_time = isoparse(self._parameters.execution_time)
        elif hasattr(self._parameters, 'get'):
            execution_time = isoparse(self._parameters.get('EXECUTION_TIME'))

        return execution_time

    def run(self):
        # pylint: disable=not-context-manager
        with self._get_client() as client:
            self._client = client

            files = self._get_files()

            resolved_files = self._resolve_files(files)

            data = self._extract_files(resolved_files)

        self._log_extracted_data_sizes("raw", data)

        self._client = None

        decoded_data = self._decode_dataset(data, resolved_files)

        self._log_extracted_data_sizes("decoded", decoded_data)

        if self.include_names:
            target_files = self._get_target_files(resolved_files)

            decoded_data = [pickle.dumps(list(zip(target_files, decoded_data)))]

        return decoded_data

    @abstractmethod
    def _get_client(self) -> 'Context Manager':
        return None

    @abstractmethod
    def _get_files(self) -> list:
        return None

    def _get_target_datetime(self):
        return self.execution_time

    def _resolve_files(self, files):
        timestamped_files = self._resolve_timestamps(files)

        expanded_files = self._resolve_wildcards(timestamped_files)

        return expanded_files

    def _extract_files(self, files):
        data = [self._extract_file(file) for file in files]

        return data

    @classmethod
    def _log_extracted_data_sizes(cls, data_type, data):
        for datum in data:
            LOGGER.debug('Extracted %s %d bytes.', data_type, len(datum))

    def _decode_dataset(self, dataset, files):
        decoded_dataset = []

        for index, data in enumerate(dataset):
            try:
                decoded_dataset.append(self._decode_data(data))
            except Exception as exception:
                raise ETLException(f'Unable to decode {files[index]}') from exception

        return decoded_dataset

    # pylint: disable=no-self-use
    def _get_target_files(self, files):
        '''Allow extractors to modify output file paths when including names.'''
        return files

    def _resolve_wildcards(self, files):
        expanded_files = []

        for file in files:
            expanded_files.extend(self._resolve_wildcard(file))

        return expanded_files

    def _resolve_timestamps(self, files):
        return [datetime.strftime(self._get_target_datetime(), file) for file in files]

    @abstractmethod
    def _extract_file(self, file):
        return []

    @classmethod
    def _decode_data(cls, data):
        return data

    @abstractmethod
    def _resolve_wildcard(self, file):
        return None
