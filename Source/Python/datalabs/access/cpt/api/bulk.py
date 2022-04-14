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
        release_directory = self._get_release_directory()
        user_directory = self._get_user_directory(release_directory)
        files_directory = '/'.join((self._parameters.bucket_base_path, release_directory[-1]))
        user_files = self._list_directory(user_directory)

        if 'files.zip' in user_files:
            files_directory = user_directory

        return '/'.join((files_directory, 'files.zip'))

    def _get_release_directory(self):
        return sorted(self._list_directory(self._parameters.bucket_base_path))

    def _get_user_directory(self, release_directory):
        return '/'.join((
            self._parameters.bucket_base_path,
            release_directory[-1],
            'Files',
            self._parameters.authorization["user_id"]
        ))

    def _list_directory(self, base_path):
        response = self._s3.list_objects_v2(Bucket=self._parameters.bucket_name, Prefix=base_path)

        objects = {x['Key'].split('/')[-1] for x in response['Contents']}

        if '' in objects:
            objects.remove('')

        return objects
