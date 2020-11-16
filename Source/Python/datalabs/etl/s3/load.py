""" AWS S3 Loader """
import base64
from   datetime import datetime
from   dateutil.parser import isoparse
import hashlib
import logging

import boto3

from   datalabs.etl.load import LoaderTask
from   datalabs.etl.task import ETLException

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class S3FileLoaderTask(LoaderTask):
    def __init__(self, parameters):
        super().__init__(parameters)

        self._s3 = boto3.client(
            's3',
            endpoint_url=self._parameters.variables.get('ENDPOINT_URL'),
            aws_access_key_id=self._parameters.get('ACCESS_KEY'),
            aws_secret_access_key=self._parameters.get('SECRET_KEY'),
            region_name=self._parameters.get('REGION_NAME')
        )

    def _load(self):
        current_path = self._get_current_path()
        files = self._parameters.variables['FILES'].split(',')

        return [self._load_file(current_path, file, data) for file, data in zip(files, self._parameters.data)]

    def _get_current_path(self):
        current_date = self._get_execution_date() or datetime.utcnow().date().strftime('%Y%m%d')

        return '/'.join((self._parameters.variables['BASEPATH'], current_date))

    def _load_file(self, base_path, file, data):
        file_path = '/'.join((base_path, file))

        try:
            body = self._encode(data)
        except Exception as exception:
            raise ETLException(f'Unable to encode S3 object {file_path}: {exception}')

        md5_hash = hashlib.md5(body).digest()
        b64_md5_hash = base64.b64encode(md5_hash)

        return self._s3.put_object(
            Bucket=self._parameters.variables['BUCKET'],
            Key=file_path,
            Body=body,
            ContentMD5=b64_md5_hash.decode('utf-8'))

    def _get_execution_date(self):
        execution_time = self._parameters.variables.get('EXECUTIONTIME')
        execution_date = None

        if execution_time:
            execution_date = isoparse(execution_time).date().strftime('%Y%m%d')

        return execution_date

    def _encode(self, data):
        return data


class S3UnicodeTextFileLoaderTask(S3FileLoaderTask):
    def _encode(self, data):
        return data.encode('utf-8', errors='backslashreplace')


class S3WindowsTextFileLoaderTask(S3FileLoaderTask):
    def _encode(self, data):
        return data.encode('cp1252', errors='backslashreplace')
