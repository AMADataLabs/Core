""" Archival Transformer classes. """
from   io import BytesIO
from   dataclasses import dataclass
import logging
import pickle
from   pathlib import Path
from   zipfile import ZipFile

from   datalabs.etl.extract import FileExtractorTask
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class UnzipTransformerParameters:
    files: str = None
    ignore_path_depth: str = None
    execution_time: str = None

class UnzipTransformerTask(FileExtractorTask):
    PARAMETER_CLASS = UnzipTransformerParameters
    @property
    def include_names(self):
        return True

    def _get_client(self) -> 'Context Manager':
        return ZipFiles(self._data)

    def _get_files(self) -> list:
        return self._client.files

    def _extract_file(self, file):
        return self._client.extract(file)

    def _get_target_files(self, files):
        target_files = files

        if self._parameters.ignore_path_depth:
            ignore_path_depth = int(self._parameters.ignore_path_depth)

            target_files = [str(Path(*Path(path).parts[ignore_path_depth:])) for path in files]

        return target_files

    def _resolve_wildcard(self, file):
        return [file]


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ZipTransformerParameters:
    execution_time: str = None


class ZipTransformerTask(Task):
    PARAMETER_CLASS = ZipTransformerParameters

    def run(self) -> 'Transformed Data':
        return [self._zip_files(pickle.loads(pickled_dataset)) for pickled_dataset in self._data]

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

    def get_info(self, file):
        zip_file = self._zip_files[self._file_zip_map[file]]

        return zip_file.getinfo(file).file_size

    def __enter__(self):
        self._zip_files = [ZipFile(BytesIO(zip_file)) for zip_file in self._zip_file_data]

        self._file_zip_map = {name:index for index, zip in enumerate(self._zip_files) for name in zip.namelist()}

        for file, index in list(self._file_zip_map.items()):
            zip_file = self._zip_files[index]

            if zip_file.getinfo(file).is_dir():
                self._file_zip_map.pop(file)

        return self

    def __exit__(self, *args, **kwargs):
        self._zip_files = None
        self._file_zip_map = None
