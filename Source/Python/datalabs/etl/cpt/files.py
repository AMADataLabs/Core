"""
searches the processed data S3 bucket for the most recent (current) and
next most recent (prior) release distribution zip files
"""
from   dataclasses import dataclass
from   datalabs.parameter import add_schema
from   datalabs.etl.s3.extract import S3FileExtractorTask

@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ReleaseFilesListExtractorParameters:
    base_path: str
    link_files_zip: str = None
    execution_time: str = None

# pylint: disable=too-many-ancestors
class ReleaseFilesListExtractorTask(S3FileExtractorTask):
    PARAMETER_CLASS = ReleaseFilesListExtractorParameters

    def _get_files(self):
        current_base_path = self._get_latest_path()
        prior_base_path = self._get_second_latest_path()
        files, current_files, prior_files = [], [], []

        if self._parameters.link_files_zip is not None:
            files = self._parameters.link_files_zip.split(',')
        else:
            raise ValueError('"files" parameter must contain the list of files to extract.')

        if current_base_path and prior_base_path:
            current_files = ['/'.join((current_base_path, file.strip())) for file in files]
            prior_files = ['/'.join((prior_base_path, file.strip())) for file in files]
            files = current_files + prior_files
        elif current_base_path:
            files = ['/'.join((current_base_path, file.strip())) for file in files]
        else:
            files = []

        return files

    def _get_latest_path(self):
        release_folder = self._get_release_folder()
        path = self._parameters.base_path

        if (release_folder is not None) and (path is not None):
            path = '/'.join((self._parameters.base_path, release_folder))

        if path.startswith('/'):
            path = path[1:]

        return path

    def _get_second_latest_path(self):
        release_folder = self._get_prior_release_folder()
        path = self._parameters.base_path

        if (release_folder is not None) and (path is not None):
            path = '/'.join((self._parameters.base_path, release_folder))

        if path.startswith('/'):
            path = path[1:]

        return path

    def _get_prior_release_folder(self):
        release_folders = sorted(
            super()._list_files(self._parameters.base_path)
        )
        release_folder = release_folders[-2]

        return release_folder
