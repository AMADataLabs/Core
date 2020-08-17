""" AWS S3 Loader """
import base64
from   datetime import datetime
import hashlib
import logging

import boto3

from datalabs.etl.load import LoaderTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class S3FileLoaderTask(LoaderTask):
    def __init__(self, parameters):
        super().__init__(parameters)

        self._s3 = boto3.client('s3')

    def _load(self):
        current_path = self._get_current_path()
        files = self._parameters.variables['FILES'].split(',')

        return [self._load_file(current_path, file, data) for file, data in zip(files, self._parameters.data)]

    def _get_current_path(self):
        current_date = datetime.utcnow().date().strftime('%Y%m%d')

        return '/'.join((self._parameters.variables['PATH'], current_date))

    def _load_file(self, base_path, file, data):
        file_path = '/'.join((base_path, file))
        body = self._encode(data)
        md5_hash = hashlib.md5(body).digest()
        b64_md5_hash = base64.b64encode(md5_hash)

        return self._s3.put_object(
            Bucket=self._parameters.variables['BUCKET'],
            Key=file_path,
            Body=body,
            ContentMD5=b64_md5_hash.decode('utf-8'))

    def _encode(self, data):
        return data


class S3UnicodeTextLoaderTask(S3FileLoaderTask):
    def _encode(self, data):
        return data.encode('utf-8')


class S3WindowsTextLoaderTask(S3FileLoaderTask):
    def _encode(self, data):
        return data.encode('cp1252')
