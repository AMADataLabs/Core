""" AWS S3 Loader """
import base64
from   dataclasses import dataclass
from   datetime import datetime
import hashlib

from   dateutil.parser import isoparse

from   datalabs.access.aws import AWSClient
from   datalabs.etl.load import FileLoaderTask, IncludesNamesMixin, CurrentPathMixin
from   datalabs.etl.task import ExecutionTimeMixin
from   datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class S3FileLoaderParameters:
    bucket: str
    base_path: str
    files: str = None
    endpoint_url: str = None
    access_key: str = None
    secret_key: str = None
    region_name: str = None
    includes_names: str = None
    include_datestamp: str = None
    execution_time: str = None
    assume_role: str = None
    on_disk: str = False


class S3FileLoaderTask(ExecutionTimeMixin, CurrentPathMixin, IncludesNamesMixin, FileLoaderTask):
    PARAMETER_CLASS = S3FileLoaderParameters

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
        current_path = self._get_current_path()

        return ['/'.join((current_path, file.strip())) for file in self._parameters.files.split(',')]

    def _load_file(self, data, file):
        response = None

        if self._parameters.on_disk and self._parameters.on_disk.upper() == 'TRUE':
            md5_hash = self._md5_file(data)

            with open(data, 'rb') as body:  # data is a filename bytes string
                response = self._put_object(file, body, md5_hash)
        else:
            md5_hash = hashlib.md5(data).digest()

            response = self._put_object(file, data, md5_hash)

        return response

    def _get_current_path(self):
        release_folder = self._get_execution_date() or datetime.utcnow().date().strftime('%Y%m%d')
        path = self._parameters.base_path

        if self._parameters.include_datestamp is None or self._parameters.include_datestamp.lower() == 'true':
            path = '/'.join((self._parameters.base_path, release_folder))

        if path.startswith('/'):
            path = path[1:]

        return path

    @classmethod
    def _md5_file(cls, path):
        hash_md5 = hashlib.md5()

        with open(path, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hash_md5.update(chunk)

        return hash_md5.digest()

    def _put_object(self, file, data, md5_hash):
        b64_md5_hash = base64.b64encode(md5_hash)

        response = self._client.put_object(
            Bucket=self._parameters.bucket,
            Key=file,
            Body=data,
            ContentMD5=b64_md5_hash.decode()
        )

        return response

    def _get_execution_date(self):
        execution_time = self._parameters.execution_time
        execution_date = None

        if execution_time:
            execution_date = isoparse(execution_time).date().strftime('%Y%m%d')

        return execution_date


# pylint: disable=too-many-ancestors
class S3WindowsTextFileLoaderTask(S3FileLoaderTask):
    def _encode_data(self, data):
        return data.decode().encode('cp1252', errors='backslashreplace')


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class S3FileReplicatorParameters(ExecutionTimeMixin):
    bucket: str
    base_path: str
    files: str = None
    endpoint_url: str = None
    access_key: str = None
    secret_key: str = None
    region_name: str = None
    includes_names: str = None
    include_datestamp: str = None
    execution_time: str = None
    assume_role: str = None
    on_disk: str = False


class S3FileReplicatorTask:
    pass
