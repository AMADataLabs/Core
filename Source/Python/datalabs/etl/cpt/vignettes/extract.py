""" Vignettes input extractors """
from   dataclasses import dataclass
from   datetime import datetime

from   dateutil.parser import isoparse

from   datalabs.access.sftp import SFTP
from   datalabs.parameter import add_schema
from   datalabs.task import Task


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class InputFilesListExtractorParameters:
    base_path: str
    username: str
    password: str
    host: str
    execution_time: str = None


# pylint: disable=too-many-ancestors
class InputFilesListExtractorTask(Task):
    PARAMETER_CLASS = InputFilesListExtractorParameters

    def run(self):
        with SFTP({'username': self._parameters.username, 'password': self._parameters.password}) as sftp:
            files = self._generate_file_names(sftp)

        joined_filenames = '\n'.join(files)

        return [joined_filenames.encode()]

    def _generate_file_names(self, sftp):
        execution_date = self._get_datestamp_from_execution_time(self._parameters.execution_time)
        current_year = execution_date[:4]
        link_year = int(current_year) - 1

        link = self._get_link_folder(sftp, self._parameters.base_path, str(link_year))

        vignettes = self._generate_vignettes_filename(current_year)
        comprehensive = self._generate_comprehensive_filename(link)
        hcpcs = self._generate_hcpcs_filename(link)
        administrative_codes = self._generate_administrative_codes_filename(link)

        return [vignettes, comprehensive, hcpcs, administrative_codes]

    @classmethod
    def _get_datestamp_from_execution_time(cls, execution_time):
        execution_date = datetime.now().strftime('%Y%m%d')

        if execution_time:
            execution_date = isoparse(execution_time).date().strftime('%Y%m%d')

        return execution_date

    @classmethod
    def _get_link_folder(cls, sftp, base_path, year):
        link_folders = sftp.list_directory(base_path + 'CPT Link/' + year)

        release_folder = next((folder for folder in link_folders if '09' in folder), None).strip('.')

        return 'CPT Link/' + year + release_folder + release_folder + '/CPT Link/extracts/'

    @classmethod
    def _generate_vignettes_filename(cls, year):
        folder = 'CPT Vignettes ' + year
        file = 'Clinical Vignettes ' + year + ' - Pipe.txt'

        return  'Clinical Vignettes Data File/' + year + '/' + folder + '/' + file

    @classmethod
    def _generate_comprehensive_filename(cls, link):
        return link + 'Comprehensive.txt'

    @classmethod
    def _generate_hcpcs_filename(cls, link):
        return link + 'HcpcsIICodes.txt'

    @classmethod
    def _generate_administrative_codes_filename(cls, link):
        return link + 'MAAA.txt'
