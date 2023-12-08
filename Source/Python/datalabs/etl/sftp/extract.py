""" Local file system extractors """
from   dataclasses import dataclass
import io
import itertools
import logging
import os

from   paramiko.sftp import SFTPError

from   datalabs.access import sftp
from   datalabs.etl.extract import FileExtractorTask, IncludeNamesMixin, TargetOffsetMixin
from   datalabs.etl.task import ETLException
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class SFTPFileExtractorParameters:
    base_path: str
    host: str
    username: str
    password: str
    files: str = None
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
        files = []

        if self._parameters.files is not None:
            files = self._parameters.files.split(',')
        elif self._data is not None and len(self._data) > 0:
            files = list(itertools.chain.from_iterable(self._parse_file_lists(self._data)))
        else:
            raise ValueError('Either the "files" or "data" parameter must contain the list of files to extract.')

        return [os.path.join(base_path, file.strip()) for file in files]

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
        data = None

        try:
            self._client.get(file, buffer)
        except Exception as exception:
            raise ETLException(f"Unable to read file '{file}'") from exception

        data =  bytes(buffer.getbuffer())
        LOGGER.info('Extracted %d byte file %s.', len(data), file)

        return data

    @classmethod
    def _parse_file_lists(cls, data, ignore_header=False):
        for raw_file_list in data:
            file_list = [file.decode().strip() for file in raw_file_list.split(b'\n')]

            if '' in file_list:
                file_list.remove('')

            if ignore_header:
                file_list = file_list[1:]

            yield file_list


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

        return "\n".join(os.path.join(directory, file.strip()) for file in list_of_files).encode()

    def _get_directory_listing(self, directory):
        try:
            list_of_files = self._client.list(directory)
        except FileNotFoundError as exception:
            raise FileNotFoundError(f"No such directory: '{directory}'") from exception
        except SFTPError as exception:
            raise ValueError(f"'files' parameter must be a directory not a file: '{directory}'") from exception

        return list_of_files
