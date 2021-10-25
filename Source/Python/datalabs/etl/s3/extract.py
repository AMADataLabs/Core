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
import logging
import tempfile
# import pickle

from   dateutil.parser import isoparse

from   datalabs.access.aws import AWSClient
from   datalabs.etl.extract import FileExtractorTask, IncludeNamesMixin
from   datalabs.etl.task import ETLException, ExecutionTimeMixin
import datalabs.feature as feature
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
    files: str
    endpoint_url: str = None
    access_key: str = None
    secret_key: str = None
    region_name: str = None
    include_names: str = None
    include_datestamp: str = None
    execution_time: str = None
    on_disk: str = False
    assume_role: str = None
    data: object = None

@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
#NOTE: HADI CHECK IF THIS IS NEEDED
class S3DirectoryListingExtractorParameters:
    bucket: str
    base_path: str
    endpoint_url: str = None
    access_key: str = None
    secret_key: str = None
    region_name: str = None
    execution_time: str = None
    on_disk: str = False
    assume_role: str = None

# pylint: disable=too-many-ancestors
class S3FileExtractorTask(IncludeNamesMixin, ExecutionTimeMixin, FileExtractorTask):
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
        files = self._parameters.files.split(',')

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
        data = None

        if feature.enabled("PROFILE"):
            LOGGER.info(f'Pre extraction memory {(hpy().heap())}')

        try:
            response = self._client.get_object(Bucket=self._parameters.bucket, Key=file)
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
        # NOTE: HADI, REMOVE THIS
        # st()
        return data

    def _get_latest_path(self):
        release_folder = self._get_release_folder()
        path = self._parameters.base_path

        if self._parameters.include_datestamp is None or self._parameters.include_datestamp.lower() == 'true':
            path = '/'.join((self._parameters.base_path, release_folder))

        return path

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

        # NOTE: HADI, ASK PETER IF TRY AND EXCEPT ARE NEEDED
        # objects = None
        # try:
        objects = {x['Key'].split('/', 3)[2] for x in response['Contents']}
        # except IndexError:
        #     objects = set()

        if  '' in objects:
            objects.remove('')

        return objects


# pylint: disable=too-many-ancestors
class S3WindowsTextFileExtractorTask(S3FileExtractorTask):
    @classmethod
    def _decode_data(cls, data):
        return data.decode('cp1252', errors='backslashreplace').encode()
