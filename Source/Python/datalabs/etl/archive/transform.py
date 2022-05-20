""" Archival Transformer classes. """
from   io import BytesIO
from   dataclasses import dataclass
import logging
import pickle
from   zipfile import ZipFile

from   datalabs.etl.transform import TransformerTask
from   datalabs.etl.extract import FileExtractorTask
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class UnzipTransformerParameters:
    data: object
    files: str = None
    execution_time: str = None


class UnzipTransformerTask(FileExtractorTask):
    PARAMETER_CLASS = UnzipTransformerParameters
    @property
    def include_names(self):
        return True

    def _get_client(self) -> 'Context Manager':
        return ZipFiles(self._parameters.data)

    def _get_files(self) -> list:
        return self._client.files

    def _extract_file(self, file):
        return self._client.extract(file)

    def _resolve_wildcard(self, file):
        return [file]


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ZipTransformerParameters:
    data: object
    execution_time: str = None


class ZipTransformerTask(TransformerTask):
    PARAMETER_CLASS = UnzipTransformerParameters

    def _transform(self) -> 'Transformed Data':
        return [self._zip_files(pickle.loads(pickled_dataset)) for pickled_dataset in self._parameters.data]

    @classmethod
    def _zip_files(cls, filename_data_tuples):
        zip_data = BytesIO()

        with ZipFile(zip_data, 'w') as zip_file:
            for file, data in filename_data_tuples:
                LOGGER.debug('Adding %s byte file %s to the archive...', len(data), file)
                zip_file.writestr(file, data)

        return bytes(zip_data.getbuffer())


class ZipFiles:
    def __init__(self, zip_files):
        self._zip_file_data = zip_files
        self._zip_files = None
        self._file_zip_map = None

    @property
    def files(self):
        return list(self._file_zip_map.keys())

    def extract(self, file):
        zip_file = self._zip_files[self._file_zip_map[file]]

        return zip_file.read(file)

    def __enter__(self):
        self._zip_files = [ZipFile(BytesIO(zip_file)) for zip_file in self._zip_file_data]

        self._file_zip_map = {name:index for index, zip in enumerate(self._zip_files) for name in zip.namelist()}

        return self

    def __exit__(self, *args, **kwargs):
        self._zip_files = None
        self._file_zip_map = None
