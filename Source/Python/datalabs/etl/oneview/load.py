"""Oneview PPD Loader Task"""
import logging

from io import BytesIO
from minio import Minio

from datalabs.etl.load import LoaderTask
from datalabs.etl.task import ETLException

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class PPDFileLoader(LoaderTask):
    def _load(self):
        self._logger.info(self._parameters.data)
        client = self._connect_to_client()

        try:
            self._upload_file(client)

        except Exception as exception:
            raise ETLException('Invalid Data') from exception

    def _connect_to_client(self):
        minioClient = Minio(self._parameter.database['ENDPOINT'],
                            access_key=self._parameters.database['ACCESS_KEY'],
                            secret_key=self._parameters.database['SECRET_KEY'],
                            secure=True
                            )
        return minioClient

    def _upload_file(self, client):
        self._make_bucket(client)

        for data, table in self._parameters.data, self._parameters.variables['TABLE_NAMES']:
            client.put_object(
                self._paramters.database['BUCKET'],
                table,
                data=BytesIO(data),
                length=len(data),
                content_type='application/csv'
            )

    def _make_bucket(self, client):
        if client.bucket_exists(self._paramters.database['BUCKET']):
            self._logger.info('Bucket exists')

        else:
            client.make_bucket(self._paramters.database['BUCKET'])
            self._logger.info('Bucket created')
