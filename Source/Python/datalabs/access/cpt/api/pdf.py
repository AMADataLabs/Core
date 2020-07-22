""" Release endpoint classes. """
import logging

import boto3

from   datalabs.access.task import APIEndpointTask, InternalServerError
from   datalabs.etl.cpt.dbmodel import Release

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ReleasesEndpointTask(APIEndpointTask):
    def _run(self, session):
        s3 = boto3.client('s3')

        try:
            response = s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self._parameters.bucket['name'],
                    'Key': 
                },
                ExpiresIn=self._parameters.bucket['url_duration']
            )
        except ClientError as e:
            LOGGER.error(e)
            raise InternalServerError(f'Unable to get PDF archive URL: {str(e)}')

    import pdb; pdb.set_trace()
    return 200, response

    def _get_latest_path(self):
        if self._latest_path is None:
            release_folders = sorted(
                self._listdir(
                    self._parameters.variables['BUCKET'],
                    self._parameters.variables['BASE_PATH']
                )
            )

            self._latest_path = '/'.join((self._parameters.variables['BASE_PATH'], release_folders[-1]))

        return self._latest_path
