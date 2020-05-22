""" Object used to extract test data for the CPT CSV ETL. """
import io

import boto3

from datalabs.etl.extract import Extractor


class S3Extractor(Extractor):
    def __init__(self, configuration):
        super().__init__(configuration)

        self._s3 = boto3.client('s3')

    def extract(self):
        latest_cpt_path = self._get_latest_cpt_path()

        return [self._extract_file(latest_cpt_path, file) for file in self._configuration['FILES']]

    def _get_latest_cpt_path(self):
        release_folders = sorted(self._listdir(self._configuration['BUCKET'], self._configuration['BASE_PATH']))

        return '/'.join((self._configuration['BASE_PATH'], release_folders[0]))

    def _extract_file(self, base_path, file):
        file_path = '/'.join((base_path, file))

        response = self._s3.get_object(Bucket=self._configuration['BUCKET'], Key=file_path)

        return response['Body'].read().decode('cp1252')

    def _listdir(self, bucket, base_path):
        response = self._s3.list_objects_v2(Bucket=bucket, Prefix=base_path)

        objects = {x['Key'].split('/', 3)[2] for x in response['Contents']}
        objects.remove('')

        return objects
