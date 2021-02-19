""" Local file system extractors """
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
    def _extract(self):
        data = None

        with self._get_sftp(self._parameters.variables) as sftp:
            file_paths = self._get_file_paths(sftp)
            logging.info('Extracting the following files via SFTP: %s', file_paths)

            data = self._extract_files(sftp, file_paths)

        return data

    def _get_file_paths(self, sftp):
        base_path = self._parameters.variables['BASE_PATH']
        unresolved_files = [os.path.join(base_path, file) for file in self._parameters.variables['FILES'].split(',')]
        # resolved_files = []

        # for file in unresolved_files:
        #     files = self._resolve_filename(sftp, file)
        #
        #     if isinstance(files, str):
        #         resolved_files.append(files)
        #     else:
        #         resolved_files += files

        return self._resolve_timestamps(unresolved_files)

    # pylint: disable=arguments-differ
    def _extract_file(self, sftp, file_path):
        buffer = io.BytesIO()

        try:
            sftp.get(file_path, buffer)
        except Exception as exception:
            raise ETLException(f"Unable to read file '{file_path}'") from exception

        return bytes(buffer.getbuffer())

    @classmethod
    def _resolve_filename(cls, sftp, file_path):
        base_path = os.path.dirname(file_path)
        unresolved_file = os.path.basename(file_path)
        file_paths = [os.path.join(base_path, file) for file in sftp.list(base_path, filter=unresolved_file)]

        if len(file_paths) == 0:
            raise FileNotFoundError(f"Unable to find file '{file_path}'")

        return file_paths

    @classmethod
    def _resolve_timestamps(cls, files):
        now = datetime.utcnow()

        return [datetime.strftime(now, file) for file in files]

    @classmethod
    def _decode_data(cls, data):
        return data


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
