""" AWS S3 Loader """
import base64
from   dataclasses import dataclass
from   datetime import datetime
import hashlib
import logging

from   dateutil.parser import isoparse

from   datalabs.access.aws import AWSClient
from   datalabs.etl.load import FileLoaderTask
from   datalabs.etl.task import ETLException, ExecutionTimeMixin
from   datalabs.task import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class S3FileLoaderParameters:
    bucket: str
    base_path: str
    files: str
    data: object
    endpoint_url: str = None
    access_key: str = None
    secret_key: str = None
    region_name: str = None
    include_datestamp: str = None
    execution_time: str = None


class S3FileLoaderTask(ExecutionTimeMixin, FileLoaderTask):
    PARAMETER_CLASS = S3FileLoaderParameters

    def _get_client(self):
        return AWSClient(
            's3',
            endpoint_url=self._parameters.endpoint_url,
            aws_access_key_id=self._parameters.access_key,
            aws_secret_access_key=self._parameters.secret_key,
            region_name=self._parameters.region_name
        )

    def _load(self):
        files = self._get_files()

        return [self._load_file(data, file) for file, data in zip(files, self._parameters.data)]

    def _get_files(self):
        current_path = self._get_current_path()

        return ['/'.join((current_path, file.strip())) for file in self._parameters.files.split(',')]

    def _load_file(self, data, file):
        try:
            body = self._encode(data)
        except Exception as exception:
            raise ETLException(f'Unable to encode S3 object {file}') from exception

        md5_hash = hashlib.md5(body).digest()
        b64_md5_hash = base64.b64encode(md5_hash)

        return self._client.put_object(
            Bucket=self._parameters.bucket,
            Key=file,
            Body=body,
            ContentMD5=b64_md5_hash.decode('utf-8'))

    def _get_current_path(self):
        release_folder = self._get_execution_date() or datetime.utcnow().date().strftime('%Y%m%d')
        path = self._parameters.base_path

        if self._parameters.include_datestamp is None or self._parameters.include_datestamp.lower() == 'true':
            path = '/'.join((self._parameters.base_path, release_folder))

        return path

    def _get_execution_date(self):
        execution_time = self._parameters.execution_time
        execution_date = None

        if execution_time:
            execution_date = isoparse(execution_time).date().strftime('%Y%m%d')

        return execution_date

    # pylint: disable=no-self-use
    def _encode(self, data):
        return data


# pylint: disable=too-many-ancestors
class S3UnicodeTextFileLoaderTask(S3FileLoaderTask):
    def _encode(self, data):
        return data.encode('utf-8', errors='backslashreplace')


# pylint: disable=too-many-ancestors
class S3WindowsTextFileLoaderTask(S3FileLoaderTask):
    def _encode(self, data):
        return data.encode('cp1252', errors='backslashreplace')
