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
        BASE_PATH="AMA/CPT",
        FILES="standard/MEDU.txt,standard/SHORTU.txt",
    }

    the following files would be extracted as strings by the S3WindowsTextExtractor:
    AMA/CPT/20200401/standard/MEDU.txt
    AMA/CPT/20200401/standard/SHORTU.txt
"""
import boto3

from datalabs.etl.extract import ExtractorTask


class S3WindowsTextExtractorTask(ExtractorTask):
    def __init__(self, parameters):
        super().__init__(parameters)

        self._s3 = boto3.client('s3')
        self._latest_path = None

    def extract(self):
        latest_path = self._get_latest_path()
        files = self._parameters['FILES'].split(',')

        return [self._extract_file(latest_path, file) for file in files]

    def _get_latest_path(self):
        if self._latest_path is None:
            release_folders = sorted(self._listdir(self._parameters['BUCKET'], self._parameters['BASE_PATH']))

            self._latest_path = '/'.join((self._parameters['BASE_PATH'], release_folders[-1]))

        return self._latest_path

    def _extract_file(self, base_path, file):
        file_path = '/'.join((base_path, file))

        response = self._s3.get_object(Bucket=self._parameters['BUCKET'], Key=file_path)

        return response['Body'].read().decode('cp1252')

    def _listdir(self, bucket, base_path):
        response = self._s3.list_objects_v2(Bucket=bucket, Prefix=base_path)

        objects = {x['Key'].split('/', 3)[2] for x in response['Contents']}

        if  '' in objects:
            objects.remove('')

        return objects
