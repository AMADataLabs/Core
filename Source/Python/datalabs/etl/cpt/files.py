"""
searches the processed data S3 bucket for the most recent (current) and
next most recent (prior) release distribution zip files
"""
from   dataclasses import dataclass

from   dateutil.parser import isoparse

from   datalabs.parameter import add_schema
from   datalabs.access.aws import AWSClient
from   datalabs.etl.extract import FileExtractorTask
from   datalabs.etl.task import ETLException


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ReleaseFilesListExtractorParameters:
    bucket: str
    base_path: str
    link_files_zip: str = None
    execution_time: str = None


# pylint: disable=too-many-ancestors
class ReleaseFilesListExtractorTask(FileExtractorTask):
    PARAMETER_CLASS = ReleaseFilesListExtractorParameters

    def _get_client(self):
        return AWSClient(
            's3'
        )

    def _get_files(self):
        current_base_path = self._get_two_latest_path()[0]
        prior_base_path = self._get_two_latest_path()[1]
        files, current_files, prior_files = [], [], []

        if self._parameters.link_files_zip is not None and (current_base_path):
            files = self._parameters.link_files_zip.split(',')
        else:
            raise ValueError('"files" parameter must contain the list of files to extract.')

        if current_base_path and prior_base_path:
            current_files = ['/'.join((current_base_path, file.strip())) for file in files]
            prior_files = ['/'.join((prior_base_path, file.strip())) for file in files]
            files = current_files + prior_files
        elif current_base_path:
            files = ['/'.join((current_base_path, file.strip())) for file in files]

        return files


    def _extract(self):
        data = None

        with self._get_client() as client:
            self._client = client
            files = self._get_files()
            data = self._extract_files(files)

        return data

    # pylint: disable=logging-fstring-interpolation
    # pylint: disable=arguments-differ
    def _extract_file(self, file):
        data = None

        try:
            response = self._client.get_object(Bucket=self._parameters.bucket, Key=file)
        except Exception as exception:
            raise ETLException(
                f"Unable to get file '{file}' from S3 bucket '{self._parameters.bucket}'"
            ) from exception

        data = response['Body'].read()

        return data

    def _extract_files(self, files):
        data = [self._extract_file(file) for file in files ]

        return data

    def _get_two_latest_path(self):
        release_folder = self._get_release_folder()
        path = self._parameters.base_path
        result_path = [None, None]

        if (release_folder is not None) and (path is not None):
            # most recent date to execution_date
            result_path[0] = '/'.join((self._parameters.base_path, release_folder[1]))
            # next most recent date to execution_date
            result_path[1] = '/'.join((self._parameters.base_path, release_folder[0]))

        if result_path[0].startswith('/'):
            result_path[0] = result_path[0][1:]
        if result_path[1].startswith('/'):
            result_path[1] = result_path[1][1:]

        return result_path

    def _get_release_folder(self):
        release_folder = self._get_execution_date()
        result = []
        list_files = sorted(self._list_files(self._parameters.base_path))

        if release_folder is not None:
            result = [d for d in list_files if d < release_folder]
            result = result[-2:]
        else:
            result = list_files[-2:]

        return result

    def _get_execution_date(self):
        execution_time = self._parameters.execution_time
        execution_date = None

        if execution_time:
            execution_date = isoparse(execution_time).date().strftime('%Y%m%d')

        return execution_date

    def _list_files(self, path):
        response = self._client.list_objects_v2(Bucket=self._parameters.bucket, Prefix=path)
        objects = {x['Key'].split('/', 3)[2] for x in response['Contents']}

        if  '' in objects:
            objects.remove('')

        return objects

    def _resolve_wildcard(self, file):
        pass
