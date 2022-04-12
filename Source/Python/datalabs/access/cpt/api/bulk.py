""" Release endpoint classes."""
import logging

import boto3
from   botocore.exceptions import ClientError

from   datalabs.access.api.task import APIEndpointTask, APIEndpointParameters, InternalServerError

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@dataclass
class FilesEndpointParameters:
    path: dict
    query: dict
    user_id: str
    user_name: str
    authorizations: dict
    bucket_name: str
    bucket_base_path: str
    bucket_url_duration: str
    unknowns: dict=None


class FilesEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = None

    def __init__(self, parameters: dict):
        super().__init__(parameters)

        self._s3 = boto3.client('s3')

    def _run(self, database):
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
        release_folders = sorted(
            self._listdir(
                self._parameters.bucket_name,
                self._parameters.bucket_base_path
            )
        )
        user_directory = '/'.join((self._parameters.bucket_base_path, release_folders[-1], 'Files', user_id))
        files_directory = '/'.join((self._parameters.bucket_base_path, release_folders[-1]))
        user_files = self._listdir(user_directory)

        if 'files.zip' in user_files:
            files_directory = user_directory

        return '/'.join((files_directory, 'files.zip'))

    def _listdir(self, bucket, base_path):
        response = self._s3.list_objects_v2(Bucket=bucket, Prefix=base_path)

        objects = {x['Key'].split('/')[-1] for x in response['Contents']}

        if '' in objects:
            objects.remove('')

        return objects
