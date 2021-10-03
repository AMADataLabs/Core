""" Release endpoint classes."""
import logging

import boto3
from   botocore.exceptions import ClientError

from   datalabs.access.api.task import APIEndpointTask, APIEndpointParameters, InternalServerError

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class FilesEndpointTask(APIEndpointTask):
    def __init__(self, parameters: APIEndpointParameters):
        super().__init__(parameters)

        self._s3 = boto3.client('s3')

    def _run(self, database):
        files_archive_path = self._get_files_archive_path()
        files_archive_url = None

        try:
            files_archive_url = self._s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self._parameters.bucket['name'],
                    'Key': files_archive_path
                },
                ExpiresIn=self._parameters.bucket['url_duration']
            )
        except ClientError as exception:
            LOGGER.error(exception)
            raise InternalServerError('Unable to get files archive URL') from exception

        self._status_code = 303
        self._headers['Location'] = files_archive_url

    def _get_files_archive_path(self):
        release_folders = sorted(
            self._listdir(
                self._parameters.bucket['name'],
                self._parameters.bucket['base_path']
            )
        )

        return '/'.join((self._parameters.bucket['base_path'], release_folders[-1], 'files.zip'))

    def _listdir(self, bucket, base_path):
        response = self._s3.list_objects_v2(Bucket=bucket, Prefix=base_path)

        objects = {x['Key'].split('/', 3)[2] for x in response['Contents']}

        if  '' in objects:
            objects.remove('')

        return objects
