""" CoreBuilderTask input extractors """
from   dataclasses import dataclass

from   dateutil.parser import isoparse

from   datalabs.access.aws import AWSClient
from   datalabs.etl.extract import ExtractorTask
from   datalabs.parameter import add_schema




@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class InputFilesListExtractorParameters:
    bucket: str
    core_base_path: str
    link_base_path: str
    execution_time: str = None


# pylint: disable=too-many-ancestors
class InputFilesListExtractorTask(ExtractorTask):
    PARAMETER_CLASS = InputFilesListExtractorParameters

    def _extract(self):
        data = None

        with AWSClient('s3') as client:
            files = self._get_files(client)

            data = self._extract_files(client, files)

        return data

    def _get_files(self, client):
        execution_date = self._get_datestamp_from_execution_time(self._parameters.execution_time)
        link_base_path = self._parameters.link_base_path
        all_link_run_paths = sorted(self._list_files(client, self._parameters.bucket, link_base_path))

        incremental_files = self._get_incremental_files(execution_date, link_base_path, all_link_run_paths)

        annual_files = self._get_annual_files(execution_date, link_base_path, all_link_run_paths)

        return incremental_files + annual_files

    def _extract_files(self, client, files):
        data = [self._extract_file(client, self._parameters.bucket, file) for file in files ]

        return data

    @classmethod
    def _get_datestamp_from_execution_time(cls, execution_time):
        execution_date = None

        if execution_time:
            execution_date = isoparse(execution_time).date().strftime('%Y%m%d')

        return execution_date

    @classmethod
    def _list_files(cls, client, bucket, path):
        response = client.list_objects_v2(Bucket=bucket, Prefix=path)
        objects = {x['Key'].split('/', 3)[2] for x in response['Contents']}

        if  '' in objects:
            objects.remove('')

        return objects

    @classmethod
    def _get_incremental_files(cls, execution_date, link_base_path, all_link_run_paths):
        link_path = cls._get_incremental_link_path(execution_date, all_link_run_paths)

        files = cls._generate_incremental_files("/".join((link_base_path,  link_path)))

        return files

    @classmethod
    def _get_annual_files(cls, execution_date, link_base_path, all_link_run_paths):
        link_path = cls._get_annual_link_path(execution_date, all_link_run_paths)

        files = cls._generate_annual_files("/".join((link_base_path,  link_path)))

        return files

    @classmethod
    def _extract_file(cls, client, bucket, file):
        data = None

        response = client.get_object(Bucket=bucket, Key=file)

        data = response['Body'].read()

        return data

    @classmethod
    def _get_incremental_link_path(cls, execution_date, all_link_run_paths):
        earlier_link_run_paths = [d for d in all_link_run_paths if d < execution_date]

        return earlier_link_run_paths[-1]

    @classmethod
    def _generate_incremental_files(cls, link_path):
        pass

    @classmethod
    def _get_annual_link_path(cls, execution_date, all_link_run_paths):
        year = str(int(execution_date[:4]) - 1)

        last_year_link_run_paths = [d for d in all_link_run_paths if d.startswith(year)]

        return last_year_link_run_paths[0]

    @classmethod
    def _generate_annual_files(cls, link_path):
        pass
