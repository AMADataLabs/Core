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


# pylint: disable=too-many-instance-attributes
@add_schema(unknowns=True)
@dataclass
class PDFsEndpointParameters:
    path: dict
    query: dict
    authorization: dict
    bucket_name: str
    bucket_base_path: str
    bucket_url_duration: str
    unknowns: dict=None


class LatestPDFsEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = PDFsEndpointParameters

    def __init__(self, parameters: dict):
        super().__init__(parameters)

        self._s3 = boto3.client('s3')

    def run(self):
        pdf_archive_path = self._get_pdf_archive_path()
        pdfs_archive_url = None

        try:
            pdfs_archive_url = self._s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self._parameters.bucket_name,
                    'Key': pdf_archive_path
                },
                ExpiresIn=self._parameters.bucket_url_duration
            )
        except ClientError as exception:
            LOGGER.error(exception)
            raise InternalServerError('Unable to get PDF archive URL') from exception

        self._status_code = 303
        self._headers['Location'] = pdfs_archive_url

    def _get_pdf_archive_path(self):
        release_folders = sorted(
            self._list_directory(
                self._parameters.bucket_name,
                self._parameters.bucket_base_path
            )
        )

        return '/'.join((self._parameters.bucket_base_path, release_folders[-1], 'pdfs.zip'))

    def _list_directory(self, bucket, base_path):
        response = self._s3.list_objects_v2(Bucket=bucket, Prefix=base_path)

        objects = {x['Key'].split('/', 3)[2] for x in response['Contents']}

        if  '' in objects:
            objects.remove('')

        return objects
