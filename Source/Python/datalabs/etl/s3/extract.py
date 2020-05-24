""" AWS S3 Extractors

    These extractors assume that objects are arranged in the S3 bucket as follows:
        SOME/BASE/PATH/YYYYMMDD/some/path/object

    It will determine the latest prefx SOME/BASE/PATH/YYYYMMDD and retrieve the objects listed in the FILES
    configuration variable. FILES is a list of S3 object names with the relative prefix some/path. For example given
    the following files in an S3 bucket named "some-bucket-name":

    AMA/CPT/20200131/standard/MEDU.txt
    AMA/CPT/20200131/standard/SHORTU.txt
    AMA/CPT/20200401/standard/MEDU.txt
    AMA/CPT/20200401/standard/SHORTU.txt

    and the following extractor configuration:

    {
        BUCKET="some-bucket-name",
        BASE_PATH="AMA/CPT",
        FILES="standard/MEDU.txt,standard/SHORTU.txt",
    }

    the following files would be extracted as strings by the S3WindowsTextExtractor:
    AMA/CPT/20200401/standard/MEDU.txt
    AMA/CPT/20200401/standard/SHORTU.txt
"""
import boto3

from datalabs.etl.extract import Extractor


class S3WindowsTextExtractor(Extractor):
    def __init__(self, configuration):
        super().__init__(configuration)

        self._s3 = boto3.client('s3')

    def extract(self):
        latest_path = self._get_latest_path()
        files = self._configuration['FILES'].split(',')

        return [self._extract_file(latest_path, file) for file in files]

    def _get_latest_path(self):
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
