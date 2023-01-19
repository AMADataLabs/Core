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

    If ASSUME_ROLE parameter is set to a RoleARN which looke liks:
    'arn:aws:iam::191296302136:role/dev-ama-apigateway-invoke-role'
    It will first assume that the ACCESS_KEY and SECRET_KEY parameters are the credentials for assuming
    a new temporary role (previously would've been set as the 'apigw' profile). Then the Extract process
    will carry on with the temporary role just assumed.
"""
from   dataclasses import dataclass
import itertools
import logging
import tempfile
from   urllib.parse import quote

from   dateutil.parser import isoparse

from   datalabs.access.aws import AWSClient
from   datalabs.etl.extract import FileExtractorTask, IncludeNamesMixin, TargetOffsetMixin
from   datalabs.etl.task import ETLException, ExecutionTimeMixin
from   datalabs import feature
from   datalabs.parameter import add_schema

if feature.enabled("PROFILE"):
    from guppy import hpy

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class S3FileExtractorParameters:
    bucket: str
    base_path: str
    files: str = None
    ignore_files_header: str = None
    include_names: str = None
    include_datestamp: str = None
    execution_time: str = None
    on_disk: str = False
    endpoint_url: str = None
    access_key: str = None
    secret_key: str = None
    region_name: str = None
    assume_role: str = None
    execution_offset: str = None


# pylint: disable=too-many-ancestors
class S3FileExtractorTask(TargetOffsetMixin, IncludeNamesMixin, FileExtractorTask):
    PARAMETER_CLASS = S3FileExtractorParameters

    def _get_client(self):
        return AWSClient(
            's3',
            endpoint_url=self._parameters.endpoint_url,
            aws_access_key_id=self._parameters.access_key,
            aws_secret_access_key=self._parameters.secret_key,
            region_name=self._parameters.region_name,
            assume_role=self._parameters.assume_role
        )

    def _get_files(self):
        base_path = self._get_latest_path()
        ignore_header = False
        files = []

        if self._parameters.ignore_files_header and self._parameters.ignore_files_header.upper() == "TRUE":
            ignore_header = True

        if self._parameters.files is not None:
            files = self._parameters.files.split(',')
        elif self._data is not None and len(self._data) > 0:
            files = list(itertools.chain.from_iterable(self._parse_file_lists(self._data, ignore_header)))
        else:
            raise ValueError('Either the "files" or "data" parameter must contain the list of files to extract.')

        files = [file.replace('"', '') for file in files]

        if base_path:
            files = ['/'.join((base_path, file.strip())) for file in files]

        return files

    def _resolve_wildcard(self, file):
        files = [file]

        if '*' in file:
            files = self._find_s3_object(file)

        if len(files) == 0:
            raise FileNotFoundError(f"Unable to find S3 object '{file}'")

        return files

    # pylint: disable=logging-fstring-interpolation
    # pylint: disable=arguments-differ
    def _extract_file(self, file):
        LOGGER.debug(f'Extracting file {file} from bucket {self._parameters.bucket}...')
        quoted_file = quote(file).replace('%2B', '+').replace('%22', '')
        data = None

        if feature.enabled("PROFILE"):
            LOGGER.info(f'Pre extraction memory {(hpy().heap())}')

        try:
            response = self._client.get_object(Bucket=self._parameters.bucket, Key=quoted_file)
        except Exception as exception:
            raise ETLException(
                f"Unable to get file '{file}' from S3 bucket '{self._parameters.bucket}'"
            ) from exception

        if self._parameters.on_disk and self._parameters.on_disk.upper() == 'TRUE':
            data = self._cache_data_to_disk(response['Body'])
        else:
            data = response['Body'].read()

        if feature.enabled("PROFILE"):
            LOGGER.info(f'Post extraction memory {(hpy().heap())}')

        return data

    def _get_latest_path(self):
        release_folder = self._get_release_folder()
        path = self._parameters.base_path

        if self._parameters.include_datestamp is None or self._parameters.include_datestamp.lower() == 'true':
            path = '/'.join((self._parameters.base_path, release_folder))

        if path.startswith('/'):
            path = path[1:]

        return path

    @classmethod
    def _parse_file_lists(cls, data, ignore_header=False):
        for raw_file_list in data:
            file_list = [file.decode().strip() for file in raw_file_list.split(b'\n')]

            if '' in file_list:
                file_list.remove('')

            if ignore_header:
                file_list = file_list[1:]

            yield file_list

    @classmethod
    def _cache_data_to_disk(cls, body):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            with open(temp_file.name, 'wb') as file:
                for chunk in body.iter_chunks(1024*1024):
                    file.write(chunk)

        return temp_file.name

    def _get_release_folder(self):
        release_folder = self._get_execution_date()

        if release_folder is None:
            release_folders = sorted(
                self._list_files(self._parameters.base_path)
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

    def _list_files(self, path):
        response = self._client.list_objects_v2(Bucket=self._parameters.bucket, Prefix=path)

        objects = {x['Key'].split('/', 3)[2] for x in response['Contents']}

        if '' in objects:
            objects.remove('')

        return objects


# pylint: disable=too-many-ancestors
class S3WindowsTextFileExtractorTask(S3FileExtractorTask):
    @classmethod
    def _decode_data(cls, data):
        return data.decode('cp1252', errors='backslashreplace').encode()


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class S3DirectoryListingExtractorParameters:
    bucket: str
    base_path: str
    directories: str
    execution_time: str = None
    endpoint_url: str = None
    access_key: str = None
    secret_key: str = None
    region_name: str = None
    assume_role: str = None


# pylint: disable=too-many-ancestors
class S3DirectoryListingExtractorTask(TargetOffsetMixin, FileExtractorTask):
    PARAMETER_CLASS = S3FileExtractorParameters

    def _get_client(self):
        return AWSClient(
            's3',
            endpoint_url=self._parameters.endpoint_url,
            aws_access_key_id=self._parameters.access_key,
            aws_secret_access_key=self._parameters.secret_key,
            region_name=self._parameters.region_name,
            assume_role=self._parameters.assume_role
        )

    def _get_files(self):
        base_path = self._parameters.base_path
        directories = self._parameters.directories.split(',')

        if base_path:
            directories = ['/'.join((base_path, directory.strip())) for directory in directories]

        return list(itertools.chain.from_iterable(self._list_files_for_each(directories)))

    def _list_files_for_each(self, paths):
        for path in paths:
            yield self._list_files(path)

    def _list_files(self, path):
        response = self._client.list_objects_v2(Bucket=self._parameters.bucket, Prefix=path)

        objects = {x['Key'].split('/', 3)[2] for x in response['Contents']}

        if  '' in objects:
            objects.remove('')

        return objects
