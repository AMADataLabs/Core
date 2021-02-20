""" Local file system extractors """
from   datetime import datetime
import io
import logging
import os

from   datalabs.access.sftp import SFTPTaskMixin
from   datalabs.etl.extract import FileExtractorTask
from   datalabs.etl.task import ETLException

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class SFTPFileExtractorTask(FileExtractorTask, SFTPTaskMixin):
    def _get_files(self):
        base_path = self._parameters.variables['BASE_PATH']

        return [os.path.join(base_path, file) for file in self._parameters.variables['FILES'].split(',')]

    def _get_client(self):
        return self._get_sftp(self._parameters.variables)

    def _resolve_wildcard(self, file):
        base_path = os.path.dirname(file)
        unresolved_file = os.path.basename(file)

        resolved_files = [os.path.join(base_path, file) for file in self._client.list(base_path, filter=unresolved_file)]

        if len(resolved_files) == 0:
            raise FileNotFoundError(f"Unable to find file '{file}'")

        return resolved_files

    # pylint: disable=arguments-differ
    def _extract_file(self, file):
        buffer = io.BytesIO()

        try:
            self._client.get(file, buffer)
        except Exception as exception:
            raise ETLException(f"Unable to read file '{file}'") from exception

        return bytes(buffer.getbuffer())


# pylint: disable=too-many-ancestors
class SFTPUnicodeTextFileExtractorTask(SFTPFileExtractorTask):
    @classmethod
    def _decode_data(cls, data):
        return data.decode('utf-8', errors='backslashreplace')


# pylint: disable=too-many-ancestors
class SFTPWindowsTextFileExtractorTask(SFTPFileExtractorTask):
    @classmethod
    def _decode_data(cls, data):
        return data.decode('cp1252', errors='backslashreplace')
