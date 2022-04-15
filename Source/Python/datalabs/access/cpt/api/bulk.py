""" Release endpoint classes."""
from   dataclasses import dataclass
import logging

import boto3
from   botocore.exceptions import ClientError

from   datalabs.access.api.task import APIEndpointTask, InternalServerError
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema(unknowns=True)
@dataclass
class FilesEndpointParameters:
    path: dict
    query: dict
    authorization: dict
    bucket_name: str
    bucket_base_path: str
    bucket_url_duration: str
    unknowns: dict=None


class FilesEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = FilesEndpointParameters

    def __init__(self, parameters: dict):
        super().__init__(parameters)

        self._s3 = boto3.client('s3')

    def run(self):
        files_archive_path = self._get_files_archive_path()
        files_archive_url = None

        try:
            files_archive_url = self._s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self._parameters.bucket_name,
                    'Key': files_archive_path
                },
                ExpiresIn=self._parameters.bucket_url_duration
            )
        except ClientError as exception:
            LOGGER.error(exception)
            raise InternalServerError('Unable to get files archive URL') from exception

        self._status_code = 303
        self._headers['Location'] = files_archive_url

    def _get_files_archive_path(self):
        all_paths = sorted(self._list_directory(self._parameters.bucket_base_path))
        latest_release_directory = self._extract_latest_release_directory(all_paths[-1])
        archive_path = '/'.join((
            latest_release_directory,
            "Files",
            self._parameters.authorization["user_id"],
            "files.zip"
        ))

        if archive_path not in all_paths:
            archive_path = '/'.join((latest_release_directory, 'files.zip'))

        return archive_path

    def _extract_latest_release_directory(self, example_path):
        relative_path = example_path.replace(f"{self._parameters.bucket_base_path}/", "")
        release_directory = relative_path.split('/')[0]

        return '/'.join((self._parameters.bucket_base_path, release_directory))

    def _list_directory(self, base_path):
        response = self._s3.list_objects_v2(Bucket=self._parameters.bucket_name, Prefix=base_path)

        return {x['Key'] for x in response['Contents']}
