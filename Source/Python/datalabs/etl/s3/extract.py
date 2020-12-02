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
        PATH="AMA/CPT",
        FILES="standard/MEDU.txt,standard/SHORTU.txt",
    }

    the following files would be extracted as strings by the S3WindowsTextExtractorTask:
    AMA/CPT/20200401/standard/MEDU.txt
    AMA/CPT/20200401/standard/SHORTU.txt
"""
import boto3
from   dateutil.parser import isoparse

from   datalabs.etl.extract import FileExtractorTask
from   datalabs.etl.task import ETLException


class S3FileExtractorTask(FileExtractorTask):
    def __init__(self, parameters):
        super().__init__(parameters)

        self._s3 = boto3.client('s3')

    def _extract(self):
        latest_path = self._get_latest_path()
        files = self._get_files(latest_path)

        return self._extract_files(self._s3, files)

    def _get_latest_path(self):
        release_folder = self._get_execution_date()

        if release_folder is None:
            release_folders = sorted(
                self._listdir(
                    self._parameters.variables['BUCKET'],
                    self._parameters.variables['BASEPATH']
                )
            )

            release_folder = release_folders[-1]

        return '/'.join((self._parameters.variables['BASEPATH'], release_folder))

    def _get_files(self, base_path):
        unresolved_files = ['/'.join((base_path, file)) for file in self._parameters.variables['FILES'].split(',')]
        resolved_files = []

        for file in unresolved_files:
            files = self._resolve_filename(file)

            if isinstance(files, str):
                resolved_files.append(files)
            else:
                resolved_files += files

        return resolved_files

    def _extract_file(self, s3, file_path):
        try:
            response = s3.get_object(Bucket=self._parameters.variables['BUCKET'], Key=file_path)
        except Exception as exception:
            raise ETLException(
                f"Unable to get file '{file_path}' from S3 bucket '{self._parameters.variables['BUCKET']}': {exception}"
            )

        return response['Body'].read()

    def _get_execution_date(self):
        execution_time = self._parameters.variables.get('EXECUTION_TIME')
        execution_date = None

        if execution_time:
            execution_date = isoparse(execution_time).date().strftime('%Y%m%d')

        return execution_date

    def _listdir(self, bucket, base_path):
        response = self._s3.list_objects_v2(Bucket=bucket, Prefix=base_path)

        objects = {x['Key'].split('/', 3)[2] for x in response['Contents']}

        if  '' in objects:
            objects.remove('')

        return objects

    def _resolve_filename(self, file_path):
        file_paths = [file_path]

        if '*' in file_path:
            file_paths = self._find_s3_object(file_path)

        if len(file_paths) == 0:
            raise FileNotFoundError(f"Unable to find S3 object '{file_path}'")

        return file_paths

    @classmethod
    def _decode_data(cls, data):
        return data

    def _find_s3_object(self, wildcard_file_path):
        file_path_parts = wildcard_file_path.split('*')
        search_results = self._s3.list_objects_v2(Bucket=self._parameters.variables['BUCKET'],
                                                   Prefix=file_path_parts[0])

        return [a['Key'] for a in search_results['Contents'] if a['Key'].endswith(file_path_parts[1])]


class S3UnicodeTextFileExtractorTask(S3FileExtractorTask):
    @classmethod
    def _decode_data(cls, data):
        return data.decode('utf-8', errors='backslashreplace')


class S3WindowsTextFileExtractorTask(S3FileExtractorTask):
    @classmethod
    def _decode_data(cls, data):
        return data.decode('cp1252', errors='backslashreplace')
