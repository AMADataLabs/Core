"""Local file system loader"""
from   dataclasses import dataclass
import logging
import os

from   datalabs.etl.load import FileLoaderTask, IncludesNamesMixin, BasePathMixin
from   datalabs.etl.task import ETLException
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class LocalFileLoaderParameters:
    base_path: str
    files: str = None
    includes_names: str = None
    execution_time: str = None


class LocalFileLoaderTask(BasePathMixin, IncludesNamesMixin, FileLoaderTask):
    PARAMETER_CLASS = LocalFileLoaderParameters

    def _get_files(self):
        base_path = self._parameters.base_path

        files = [os.path.join(base_path, file.strip()) for file in self._parameters.files.split(',')]

        return files

    def _get_client(self):
        class DummyFSClient:
            def __enter__(self):
                pass

            def __exit__(self, *args, **kwargs):
                pass

        return DummyFSClient()

    def _load_file(self, data, file):
        LOGGER.info('Writing file %s to the local file system...', file)
        parent = os.path.dirname(file)

        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(file, 'wb') as _file:
            _file.write(data)

        return data

    @classmethod
    def _encode_data(cls, data):
        return data


class LocalWindowsTextFileLoaderTask(LocalFileLoaderTask):
    @classmethod
    def _encode_data(cls, data):
        return data.decode().encode('cp1252', errors='backslashreplace')
