"""Local file system loader"""
from   dataclasses import dataclass
import os

from   datalabs.etl.load import FileLoaderTask, IncludesNamesMixin, BasePathMixin
from   datalabs.etl.task import ETLException
from   datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class LocalFileLoaderParameters:
    base_path: str
    data: list
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
        try:
            with open(file, 'wb') as _file:
                _file.write(data)
        except Exception as exception:
            raise ETLException(f"Unable to write file '{file}'") from exception

        return data

    @classmethod
    def _encode_data(cls, data):
        return data


class LocalWindowsTextFileLoaderTask(LocalFileLoaderTask):
    @classmethod
    def _encode_data(cls, data):
        return data.decode().encode('cp1252', errors='backslashreplace')
