""" Release endpoint classes."""
from   dataclasses import dataclass
from   datetime import datetime, timezone
import logging
import re

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
        release = self._parameters.query.get('release')
        target_year = self._get_target_year_from_release(release)
        authorized = self._authorized(self._parameters.authorization, target_year)
        self._status_code = 403

        if authorized:
            self._status_code = 303
            self._headers['Location'] = self._generate_presigned_url(target_year)

    @classmethod
    def _get_target_year_from_release(cls, release):
        target_year = current_time = datetime.now(timezone.utc).year

        if release is not None:
            release_parts = release.split('-')

            target_year = int(release_parts[-1])

        return target_year

    @classmethod
    def _authorized(cls, authorizations, target_year):
        authorized_years = self._get_authorized_years(authorizations)

        if target_year in authorized_years:
            return True

    def _get_files_archive_path(self, target_year):
        all_paths = sorted(self._list_directory(self._parameters.bucket_base_path, target_year))
        release_directory = self._extract_latest_release_directory(all_paths[-1], target_year)

        archive_path = '/'.join((
            release_directory,
            self._parameters.authorization["user_id"],
            "files.zip"
        ))

        if archive_path not in all_paths:
            archive_path = '/'.join((latest_release_directory, 'files.zip'))

        return archive_path

    def _generate_presigned_url(target_year):
        files_archive_path = self._get_files_archive_path(target_year)
        files_archive_url = None

        LOGGER.info('Creating presigned URL for file s3://%s/%s', self._parameters.bucket_name, files_archive_path)

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

        return files_archive_url

    @classmethod
    def _get_authorized_years(cls, authorizations):
        cpt_api_authorizations = {key:value for key, value in authorizations.items() if key.startswith('CPTAPI')}
        current_time = datetime.now(timezone.utc)
        authorized_years = []

        for name, end_datestamp in authorizations.items():
            '''Authorizations are of the form CPTAPIYY: YYYY-MM-DD-hh:mm'''
            year = int('20' + name[len('CPTAPI'):])
            end_date = datetime.strptime('%Y-%m-%d-%M:%S')

            if current_time < end_date:
                authorized_years.append(year)

    def _extract_latest_release_directory(self, example_path, target_year):
        relative_path = re.sub(f'^{self._parameters.bucket_base_path}', '', example_path)
        relative_release_directory = relative_path.split('/')[0]
        release_directory = relative_release_directory

        if len(self._parameters.bucket_base_path) > 0:
            release_directory = '/'.join((self._parameters.bucket_base_path, release_directory))

        return release_directory(self._parameters.bucket_base_path, release_directory))

    def _list_directory(self, base_path, target_year):
        response = self._s3.list_objects_v2(Bucket=self._parameters.bucket_name, Prefix=f'{base_path}/{target_year}')
        files = []

        if "Contents" in response:
            files = {x["Key"] for x in response["Contents"]}

        return files
