""" Local file system extractors """
from   dataclasses import dataclass
import io
import logging
import os

from   pandas import Series
from   paramiko.sftp import SFTPError

from   datalabs.access import sftp
from   datalabs.etl.extract import FileExtractorTask, IncludeNamesMixin, TargetOffsetMixin
from   datalabs.etl.task import ETLException, ExecutionTimeMixin
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class SFTPFileExtractorParameters:
    base_path: str
    files: str
    host: str
    username: str
    password: str
    execution_time: str = None
    include_names: str = None
    execution_offset: str = None


# pylint: disable=too-many-ancestors
class SFTPFileExtractorTask(TargetOffsetMixin, IncludeNamesMixin, FileExtractorTask):
    PARAMETER_CLASS = SFTPFileExtractorParameters

    def _get_client(self):
        sftp_parameters = dict(
            host=self._parameters.host,
            username=self._parameters.username,
            password=self._parameters.password
        )

        return sftp.SFTP(sftp_parameters)

    def _get_files(self):
        base_path = self._parameters.base_path

        return [os.path.join(base_path, file.strip()) for file in self._parameters.files.split(',')]

    def _resolve_wildcard(self, file):
        resolved_files = [file]

        if '*' in file:
            file_parts = file.split('*')
            base_path = os.path.dirname(file_parts[0])
            unresolved_file = f'{os.path.basename(file_parts[0])}*{file_parts[1]}'
            matched_files = self._client.list(base_path, filter=unresolved_file)
            resolved_files = [os.path.join(base_path, file) for file in matched_files]

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
class SFTPWindowsTextFileExtractorTask(SFTPFileExtractorTask):
    @classmethod
    def _decode_data(cls, data):
        return data.decode('cp1252', errors='backslashreplace').encode()


class SFTPIBM437TextFileExtractorTask(SFTPFileExtractorTask):
    @classmethod
    def _decode_data(cls, data):
        return data.decode('ibm437', errors='backslashreplace').encode()


class SFTPDirectoryListingExtractorTask(SFTPFileExtractorTask):
    """
    SFTP Directory Listing Extractor.
    Will create a csv file containing the list of files in a directory.

    Args (ETL parameters):
        files:
            Is the paths separated by commad which will look for the files in it.
            Will raise 'FileNotFoundError' Exception if the directory doesn't exist.
            Will raise 'paramiko.sftp.SFTPError' Exception if the value
            is a file instead of a directory.
        example:
        "Path1/,   , / ,Some/Path"
        In the example it's clear that spaces and the '/' in the end don't matter.
        So, ' ' and '/' are the same and mean the root directory.

        base_path:
            It must be set to "./"

        Except 'base_path' which was removed from the arguments,
        other Arguments have the same functionality as SFTPFileExtractorTask.
    """

    PARAMETER_CLASS = SFTPFileExtractorParameters

    def _resolve_wildcard(self, file):
        resolved_files = [file]

        if '*' in file:
            file_parts = file.split('*')
            base_path = os.path.dirname(file_parts[0])
            unresolved_file = f'{os.path.basename(file_parts[0])}*{file_parts[1]}'
            matched_files = self._client.list_directory(base_path, filter=unresolved_file)
            resolved_files = [os.path.join(base_path, file) for file in matched_files]

            if len(resolved_files) == 0:
                raise FileNotFoundError(f"Unable to find directory '{file}'")

        return resolved_files

    def _extract_file(self, file):
        directory = file
        list_of_files = self._get_directory_listing(directory)

        return bytes(
            Series(list_of_files)\
                .astype(str)\
                .rename("list_of_files")\
                .str.slice(start=2)\
                .apply(lambda cell: os.path.join(directory, cell))\
                .to_csv(index=False),
            encoding='utf-8'
        )

    def _get_directory_listing(self, directory):
        try:
            list_of_files = self._client.list(directory)
        except FileNotFoundError as exception:
            raise FileNotFoundError(f"No such directory: '{directory}'") from exception
        except SFTPError as exception:
            raise ValueError(f"'files' parameter must be a directory not a file: '{directory}'") from exception

        return list_of_files
