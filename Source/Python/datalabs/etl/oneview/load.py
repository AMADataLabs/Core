"""Oneview PPD Loader Task"""
import boto3
import logging

from datalabs.etl.load import LoaderTask
from datalabs.etl.task import ETLException
from datalabs.etl.s3.load import S3FileLoaderTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class PPDFileLoader(S3FileLoaderTask, LoaderTask):
    def __init__(self, parameters):
        self.s3 = boto3.client('s3',
                               endpoint_url=self._parameters.variables['ENDPOINT_URL'],
                               aws_access_key_id=self._parameters.variables['ACCESS_KEY'],
                               aws_secret_access_key=self._parameters.variable['SECRET_KEY'],
                               region_name='us-west-2'
                               )