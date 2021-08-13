""" Local file system extractors """
from   dataclasses import dataclass
from   glob import glob
import os

from   datalabs.etl.extract import FileExtractorTask, IncludeNamesMixin
from   datalabs.etl.task import ETLException, ExecutionTimeMixin
from   datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class LocalFileExtractorParameters:
    base_path: str
    files: str
    include_names: str = None
    execution_time: str = None


# pylint: disable=too-many-ancestors
class LocalFileExtractorTask(IncludeNamesMixin, ExecutionTimeMixin, FileExtractorTask):
    PARAMETER_CLASS = LocalFileExtractorParameters

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

    def _resolve_wildcard(self, file):
        files = glob(file)

        if len(files) == 0:
            raise FileNotFoundError(f"Unable to find file '{file}'")

        return files

    def _extract_file(self, file):
        data = None

        try:
            with open(file, 'rb') as fileref:
                data = fileref.read()
        except Exception as exception:
            raise ETLException(f"Unable to read file '{file}'") from exception

        return data


# pylint: disable=too-many-ancestors
class LocalWindowsTextFileExtractorTask(LocalFileExtractorTask):
    @classmethod
    def _decode_data(cls, data):
        return data.decode('cp1252', errors='backslashreplace').encode()
