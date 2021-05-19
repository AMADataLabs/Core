""" Loader base class """
from   datetime import datetime
import logging

from abc import ABC, abstractmethod

from datalabs.etl.task import ETLException, ETLComponentTask


class LoaderTask(ETLComponentTask, ABC):
    def run(self):
        self._load()

    @abstractmethod
    def _load(self):
        pass


class ConsoleLoaderTask(LoaderTask):
    def __init__(self, parameters):
        super().__init__(parameters)

        self._logger = logging.getLogger(ConsoleLoaderTask.__name__)
        self._logger.setLevel(logging.INFO)

    def _load(self):
        try:
            for datum in self._parameters['data']:
                self._logger.info(datum)
        except Exception:  # pylint: disable=broad-except
            self._logger.info(self._parameters['data'])


class FileLoaderTask(LoaderTask, ABC):
    def __init__(self, parameters):
        super().__init__(parameters)

        self._client = None
        self._execution_time = self.execution_time

    @property
    def execution_time(self):
        return datetime.utcnow()

    def _load(self):
        # pylint: disable=not-context-manager
        with self._get_client() as client:
            self._client = client

            files = self._get_files()

            resolved_files = self._resolve_files(files)

            encoded_data = self._encode_dataset(self._parameters.data, resolved_files)

            data = self._load_files(encoded_data, resolved_files)

        self._client = None

        return data

    @abstractmethod
    def _get_client(self) -> 'Context Manager':
        return None

    @abstractmethod
    def _get_files(self) -> list:
        return None

    def _resolve_files(self, files):
        timestamped_files = self._resolve_timestamps(files)

        return timestamped_files

    def _load_files(self, data, files):
        data = [self._load_file(data, file) for file, data in zip(files, data)]

        return data

    def _encode_dataset(self, dataset, files):
        encoded_dataset = []

        for index, data in enumerate(dataset):
            try:
                encoded_dataset.append(self._encode_data(data))
            except Exception as exception:
                raise ETLException(f'Unable to encode {files[index]}') from exception

        return encoded_dataset

    def _resolve_timestamps(self, files):
        return [datetime.strftime(self._execution_time, file) for file in files]

    @abstractmethod
    def _load_file(self, data, file):
        return []

    @classmethod
    def _encode_data(cls, data):
        return data
