""" AWS S3 Extractors

    These extractors assume that objects are arranged in the S3 bucket as follows:
        SOME/BASE/PATH/YYYYMMDD/some/path/object

    It will determine the latest prefx SOME/BASE/PATH/YYYYMMDD and retrieve the objects listed in the FILES
    parameters variable. FILES is a list of S3 object names with the relative prefix some/path. For example given
    the following files in an S3 bucket named "some-bucket-name":

    AMA/CPT/20200131/standard/MEDU.txt
    AMA/CPT/20200131/standard/SHORTU.txt
    AMA/CPT/20200401/standard/MEDU.txt
    AMA/CPT/20200401/standard/SHORTU.txt

    and the following extractor parameters:

    {
        BUCKET="some-bucket-name",
        PATH="AMA/CPT",
        FILES="standard/MEDU.txt,standard/SHORTU.txt",
    }

    the following files would be extracted as strings by the S3WindowsTextExtractorTask:
    AMA/CPT/20200401/standard/MEDU.txt
    AMA/CPT/20200401/standard/SHORTU.txt
"""
from   dataclasses import dataclass

from   dateutil.parser import isoparse

from   datalabs.access.aws import AWSClient
from   datalabs.etl.extract import FileExtractorTask, IncludeNamesMixin, ExecutionTimeMixin
from   datalabs.etl.task import ETLException
from   datalabs.task import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class S3FileExtractorParameters:
    bucket: str
    base_path: str
    files: str
    endpoint_url: str = None
    access_key: str = None
    secret_key: str = None
    region_name: str = None
    include_names: str = None
    include_datestamp: str = None
    execution_time: str = None
    data: object = None


# pylint: disable=too-many-ancestors
class S3FileExtractorTask(IncludeNamesMixin, ExecutionTimeMixin, FileExtractorTask):
    PARAMETER_CLASS = S3FileExtractorParameters

    def _get_files(self):
        base_path = self._get_latest_path()

        return ['/'.join((base_path, file.strip())) for file in self._parameters.files.split(',')]

    def _get_client(self):
        return AWSClient(
            's3',
            endpoint_url=self._parameters.endpoint_url,
            aws_access_key_id=self._parameters.access_key,
            aws_secret_access_key=self._parameters.secret_key,
            region_name=self._parameters.region_name
        )

    def _resolve_wildcard(self, file):
        files = [file]

        if '*' in file:
            files = self._find_s3_object(file)

        if len(files) == 0:
            raise FileNotFoundError(f"Unable to find S3 object '{file}'")

        return files

    # pylint: disable=arguments-differ
    def _extract_file(self, file):
        try:
            response = self._client.get_object(Bucket=self._parameters.bucket, Key=file)
        except Exception as exception:
            raise ETLException(
                f"Unable to get file '{file}' from S3 bucket '{self._parameters.bucket}'"
            ) from exception

        return response['Body'].read()

    def _get_latest_path(self):
        release_folder = self._get_release_folder()
        path = self._parameters.base_path

        if self._parameters.include_datestamp is None or self._parameters.include_datestamp.lower() == 'true':
            path = '/'.join((self._parameters.base_path, release_folder))

        return path

    def _get_release_folder(self):
        release_folder = self._get_execution_date()

        if release_folder is None:
            release_folders = sorted(
                self._listdir(
                    self._parameters.bucket,
                    self._parameters.base_path
                )
            )

            release_folder = release_folders[-1]

        return release_folder

    def _find_s3_object(self, wildcard_file_path):
        file_path_parts = wildcard_file_path.split('*')
        search_results = self._client.list_objects_v2(
            Bucket=self._parameters.bucket,
            Prefix=file_path_parts[0]
        )

        return [a['Key'] for a in search_results['Contents'] if a['Key'].endswith(file_path_parts[1])]

    def _get_execution_date(self):
        execution_time = self._parameters.execution_time
        execution_date = None

        if execution_time:
            execution_date = isoparse(execution_time).date().strftime('%Y%m%d')

        return execution_date

    def _listdir(self, bucket, base_path):
        response = self._client.list_objects_v2(Bucket=bucket, Prefix=base_path)

        objects = {x['Key'].split('/', 3)[2] for x in response['Contents']}

        if  '' in objects:
            objects.remove('')

        return objects


# pylint: disable=too-many-ancestors
class S3UnicodeTextFileExtractorTask(S3FileExtractorTask):
    @classmethod
    def _decode_data(cls, data):
        return data.decode('utf-8', errors='backslashreplace')


# pylint: disable=too-many-ancestors
class S3WindowsTextFileExtractorTask(S3FileExtractorTask):
    @classmethod
    def _decode_data(cls, data):
        return data.decode('cp1252', errors='backslashreplace')
