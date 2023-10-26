""" Release endpoint classes."""
from   dataclasses import dataclass
import logging

import boto3
from   botocore.exceptions import ClientError
from   sqlalchemy.orm.exc import NoResultFound

from   datalabs.access.api.task import APIEndpointTask, InternalServerError, ResourceNotFound
from   datalabs.access.cpt.api.authorize import ProductCode, AuthorizedAPIMixin
from   datalabs.access.orm import Database
from   datalabs.model.cpt.api import Release
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=too-many-instance-attributes
@add_schema(unknowns=True)
@dataclass
class FilesEndpointParameters:
    method: str
    path: dict
    query: dict
    authorization: dict
    database_name: str
    database_backend: str
    database_host: str
    database_port: str
    database_username: str
    database_password: str
    bucket_name: str
    bucket_base_path: str
    bucket_url_duration: str
    unknowns: dict=None


class FilesEndpointTask(AuthorizedAPIMixin, APIEndpointTask):
    PARAMETER_CLASS = FilesEndpointParameters
    PRODUCT_CODE = ProductCode.CODE_SET

    def __init__(self, parameters: dict, data: "list<bytes>"=None):
        super().__init__(parameters, data)

        self._s3 = boto3.client('s3')

    def run(self):
        LOGGER.debug('Parameters: %s', self._parameters)
        with Database.from_parameters(self._parameters) as database:
            self._run(database)

    def _run(self, database):
        release = self._get_release_parameter(self._parameters.query, database)
        code_set = self._get_release_code_set(release, database)
        authorized = self._authorized(self._parameters.authorization["authorizations"], code_set)
        self._status_code = 403
        LOGGER.debug('Code set: %s', code_set)
        LOGGER.debug('Authorized: %s', authorized)

        if authorized:
            self._status_code = 303
            self._headers['Location'] = self._generate_presigned_url(release, code_set, database)

        LOGGER.debug('Status Code: %s', self._status_code)

    @classmethod
    def _get_release_parameter(cls, parameters, database):
        release = parameters.get('release')

        if release and len(release) > 0:
            release = release[0]
        else:
            release = database.query(Release).order_by(Release.date.desc()).first().id

        return release

    @classmethod
    def _get_release_code_set(cls, release_id, database):
        release = None

        try:
            release = database.query(Release).filter(Release.id == release_id).one()
        except NoResultFound:
            # pylint: disable=raise-missing-from
            raise ResourceNotFound(f'No release for ID "{release_id}".')

        return release.code_set

    def _generate_presigned_url(self, release, target_year, database):
        files_archive_path = None
        files_archive_url = None

        if release:
            files_archive_path = self._get_files_archive_path_from_release(release, database)
        else:
            files_archive_path = self._get_files_archive_path(target_year, database)

        LOGGER.info('Creating presigned URL for file s3://%s/%s', self._parameters.bucket_name, files_archive_path)

        try:
            files_archive_url = self._s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self._parameters.bucket_name,
                    'Key': files_archive_path
                },
                ExpiresIn=self._parameters.bucket_url_duration,
                ResponseContentDisposition='attachment; filename="files.zip"'
            )
        except ClientError as exception:
            LOGGER.error(exception)
            raise InternalServerError('Unable to get files archive URL') from exception

        return files_archive_url

    def _get_files_archive_path_from_release(self, release, database):
        release_date = self._get_release_date(release, database)
        release_directory = release_date.strftime("%Y%m%d")

        return self._get_files_archive_path_for_user(release_directory, self._parameters.authorization["user_id"])

    def _get_files_archive_path(self, target_year, database):
        release_date = self._get_latest_release_for_year(target_year, database)
        release_directory = release_date.strftime("%Y%m%d")

        return self._get_files_archive_path_for_user(release_directory, self._parameters.authorization["user_id"])

    @classmethod
    def _get_release_date(cls, release_id, database):
        release = database.query(Release).filter(Release.id == release_id).one()

        return release.date

    @classmethod
    def _get_latest_release_for_year(cls, target_year, database):
        query = database.query(Release).filter(Release.id.like(f"%{target_year}")).order_by(Release.date.desc())
        latest_release = query.first()

        return latest_release.date

    def _get_files_archive_path_for_user(self, release_directory, user_id):
        archive_path = '/'.join((release_directory, user_id, "files.zip"))

        if not self._list_files(archive_path):
            archive_path = '/'.join((release_directory, 'files.zip'))

        if self._parameters.bucket_base_path:
            archive_path = self._parameters.bucket_base_path + archive_path

        return archive_path
