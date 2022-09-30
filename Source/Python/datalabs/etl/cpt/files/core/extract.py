""" CoreBuilderTask input extractors """
from   dataclasses import dataclass

from   dateutil.parser import isoparse

from   datalabs.access.aws import AWSClient
from   datalabs.etl.cpt.files.core.input import SOURCE_FILES
from   datalabs.etl.extract import ExtractorTask
from   datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class InputFilesListExtractorParameters:
    bucket: str
    base_path: str
    execution_time: str = None


# pylint: disable=too-many-ancestors
class InputFilesListExtractorTask(ExtractorTask):
    PARAMETER_CLASS = InputFilesListExtractorParameters

    def _extract(self):
        data = None

        with AWSClient('s3') as client:
            files = self._get_files(client)

        return files

    def _get_files(self, client):
        execution_date = self._get_datestamp_from_execution_time(self._parameters.execution_time)
        base_path = self._parameters.base_path
        all_core_run_paths = sorted(self._list_files(client, self._parameters.bucket, base_path))

        incremental_files = self._get_incremental_files(execution_date, base_path, all_core_run_paths)

        annual_files = self._get_annual_files(execution_date, base_path, all_core_run_paths)

        return incremental_files + annual_files

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
    def _get_incremental_files(cls, execution_date, base_path, all_core_run_paths):
        core_path = cls._get_incremental_core_path(execution_date, all_core_run_paths)

        files = cls._generate_incremental_files("/".join((base_path,  core_path)))

        return files

    @classmethod
    def _get_annual_files(cls, execution_date, base_path, all_core_run_paths):
        core_path = cls._get_annual_core_path(execution_date, all_core_run_paths)

        files = cls._generate_annual_files("/".join((base_path,  core_path)))

        return files

    @classmethod
    def _get_incremental_core_path(cls, execution_date, all_core_run_paths):
        earlier_link_run_paths = [path for path in all_core_run_paths if path < execution_date]

        return earlier_link_run_paths[-1]

    @classmethod
    def _generate_incremental_files(cls, core_path):
        return ["/".join((core_path, file)) for file in SOURCE_FILES]

    @classmethod
    def _get_annual_core_path(cls, execution_date, all_core_run_paths):
        year = str(int(execution_date[:4]) - 1)

        last_year_link_run_paths = [path for path in all_core_run_paths if path.startswith(year)]

        return last_year_link_run_paths[-1]

    @classmethod
    def _generate_annual_files(cls, core_path):
        return ["/".join((core_path, file)) for file in SOURCE_FILES]
