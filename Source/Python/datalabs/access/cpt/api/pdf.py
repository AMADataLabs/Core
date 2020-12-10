""" Release endpoint classes."""
import boto3
import logging

from   datalabs.access.api.task import APIEndpointTask, APIEndpointParameters, InternalServerError

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class LatestPDFsEndpointTask(APIEndpointTask):
    def __init__(self, parameters: APIEndpointParameters):
        super().__init__(parameters)

        self._s3 = boto3.client('s3')

    def _run(self, session):
        pdf_archive_path = self._get_pdf_archive_path()
        pdfs_archive_url = None

        try:
            pdfs_archive_url = self._s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self._parameters.bucket['name'],
                    'Key': pdf_archive_path
                },
                ExpiresIn=self._parameters.bucket['url_duration']
            )
        except ClientError as exception:
            LOGGER.error(exception)
            raise InternalServerError(f'Unable to get PDF archive URL: {str(exception)}')

        self._status_code = 303
        self._headers['Location'] = pdfs_archive_url

    def _get_pdf_archive_path(self):
        release_folders = sorted(
            self._listdir(
                self._parameters.bucket['name'],
                self._parameters.bucket['base_path']
            )
        )

        return '/'.join((self._parameters.bucket['base_path'], release_folders[-1], 'pdfs.zip'))

    def _listdir(self, bucket, base_path):
        response = self._s3.list_objects_v2(Bucket=bucket, Prefix=base_path)

        objects = {x['Key'].split('/', 3)[2] for x in response['Contents']}

        if  '' in objects:
            objects.remove('')

        return objects
