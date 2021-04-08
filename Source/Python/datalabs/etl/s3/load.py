""" AWS S3 Loader """
import base64
from   dataclasses import dataclass
from   datetime import datetime
import hashlib
import logging

import boto3
from   dateutil.parser import isoparse

from   datalabs.etl.load import LoaderTask
from   datalabs.etl.task import ETLException
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
    execution_time: str = None


class S3FileLoaderTask(LoaderTask):
    PARAMETER_CLASS = S3FileLoaderParameters

    def __init__(self, parameters):
        super().__init__(parameters)

        self._s3 = boto3.client(
            's3',
            endpoint_url=self._parameters.endpoint_url,
            aws_access_key_id=self._parameters.access_key,
            aws_secret_access_key=self._parameters.secret_key,
            region_name=self._parameters.region_name
        )

    def _load(self):
        files = self._get_files()

        return [self._load_file(file, data) for file, data in zip(files, self._parameters.data)]

    def _get_files(self):
        current_path = self._get_current_path()

        return ['/'.join((current_path, file.strip())) for file in self._parameters.files.split(',')]

    def _load_file(self, file, data):
        try:
            body = self._encode(data)
        except Exception as exception:
            raise ETLException(f'Unable to encode S3 object {file}') from exception

        md5_hash = hashlib.md5(body).digest()
        b64_md5_hash = base64.b64encode(md5_hash)

        return self._s3.put_object(
            Bucket=self._parameters.bucket,
            Key=file,
            Body=body,
            ContentMD5=b64_md5_hash.decode('utf-8'))

    def _get_current_path(self):
        current_date = self._get_execution_date() or datetime.utcnow().date().strftime('%Y%m%d')

        return '/'.join((self._parameters.base_path, current_date))

    def _get_execution_date(self):
        execution_time = self._parameters.execution_time
        execution_date = None

        if execution_time:
            execution_date = isoparse(execution_time).date().strftime('%Y%m%d')

        return execution_date

    # pylint: disable=no-self-use
    def _encode(self, data):
        return data


class S3UnicodeTextFileLoaderTask(S3FileLoaderTask):
    def _encode(self, data):
        return data.encode('utf-8', errors='backslashreplace')


class S3WindowsTextFileLoaderTask(S3FileLoaderTask):
    def _encode(self, data):
        return data.encode('cp1252', errors='backslashreplace')
