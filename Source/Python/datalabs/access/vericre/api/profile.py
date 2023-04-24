""" Release endpoint classes."""
from dataclasses import dataclass
import io
import json
import logging
import os
import shutil
import urllib.parse
import zipfile
import urllib3

from botocore.exceptions import ClientError
from sqlalchemy import func, literal, Integer

from datalabs.access.api.task import APIEndpointTask, ResourceNotFound, InternalServerError
from datalabs.access.aws import AWSClient
from datalabs.access.orm import Database
from datalabs.model.vericre.api import User, FormField, Document, Physician, Form, FormSection, FormSubSection
from datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class HttpClient:
    HTTP = urllib3.PoolManager()

class TaskParameters:
    DOCUMENT_TEMP_DIRECTORY = '/tmp/vericre_api_documents'


@add_schema(unknowns=True)
@dataclass
# pylint: disable=too-many-instance-attributes
class ProfileDocumentsEndpointParameters:
    path: dict
    query: dict
    authorization: dict
    database_name: str
    database_backend: str
    database_host: str
    database_port: str
    database_username: str
    database_password: str
    document_bucket_name: str
    unknowns: dict = None


class ProfileDocumentsEndpointTask(APIEndpointTask, TaskParameters):
    PARAMETER_CLASS = ProfileDocumentsEndpointParameters

    def run(self):
        LOGGER.debug('Parameters in ProfileDocumentsEndpointTask: %s', self._parameters)

        with Database.from_parameters(self._parameters) as database:
            self._run(database)

    def _run(self, database):
        entity_id = self._parameters.path.get('entityId')

        sub_query = self._sub_query_for_documents(database)

        sub_query = self._filter(sub_query, entity_id)

        query = self._query_for_documents(database, sub_query)

        query_result = [row._asdict() for row in query.all()]

        self._download_files_for_profile(query_result, entity_id)

        zip_file_in_bytes = self._zip_downloaded_files(entity_id)

        self._response_body = self._generate_response_body(zip_file_in_bytes)
        self._headers = self._generate_headers(entity_id)

    @classmethod
    def _sub_query_for_documents(cls, database):
        return database.query(
            User.id.label('user_id'),
            FormField.name.label('field_name'),
            User.avatar_image,
            Document.document_name,
            Document.document_path
        ).join(
            Physician, User.id == Physician.user
        ).join(
            Form, Form.id == Physician.form
        ).join(
            FormSection, FormSection.form == Form.id
        ).join(
            FormSubSection, FormSubSection.form_section == FormSection.id
        ).join(
            FormField, FormField.form_sub_section == FormSubSection.id
        ).join(
            Document, Document.id == func.cast(FormField.values[0], Integer)
        )

    def _filter(self, query, entity_id):
        query = self._filter_by_entity_id(query, entity_id)

        return query.filter(FormField.type == 'FILE').filter(Document.is_deleted == 'False')

    @classmethod
    def _filter_by_entity_id(cls, query, entity_id):
        # query me_number temporary and will update to filter by ama_entity_id in next sprint
        return query.filter(User.ama_me_number == entity_id)

    @classmethod
    def _query_for_documents(cls, database, sub_query):
        subquery = sub_query.subquery()

        return database.query(
            subquery.columns.field_name.label('document_identifier'),
            subquery.columns.document_name,
            func.concat(
                subquery.columns.user_id,
                '/',
                subquery.columns.document_path
            ).label('document_path')
        ).union(
            database.query(
                literal('Profile Avatar').label('document_identifier'),
                subquery.columns.avatar_image,
                func.concat(
                    subquery.columns.user_id,
                    '/',
                    'Avatar'
                ).label('document_path')
            )
        )

    def _download_files_for_profile(self, query_result, entity_id):
        if len(query_result) == 0:
            raise ResourceNotFound('No file found for the given entity ID')

        self._create_folder_for_downloaded_files(entity_id)

        for file in query_result:
            self._get_files_from_s3(entity_id, file)

    def _create_folder_for_downloaded_files(self, entity_id):
        os.makedirs(f'{self.DOCUMENT_TEMP_DIRECTORY}/{entity_id}')

    def _get_files_from_s3(self, entity_id, file):
        document_name = file['document_name']
        encoded_document_name = urllib.parse.quote(
            file['document_name'],
            safe=' '
        ).replace(" ", "+")
        document_key = f"{file['document_path']}/{encoded_document_name}"

        try:
            with AWSClient('s3') as aws_s3:
                aws_s3.download_file(
                    Bucket=self._parameters.document_bucket_name,
                    Key=document_key,
                    Filename=f"{self.DOCUMENT_TEMP_DIRECTORY}/{entity_id}/{document_name}"
                )

                LOGGER.info("%s/%s downloaded.", entity_id, document_name)
        except ClientError as error:
            LOGGER.exception(error.response)

    def _zip_downloaded_files(self, entity_id):
        folder_to_zip = f'{self.DOCUMENT_TEMP_DIRECTORY}/{entity_id}'
        zip_file_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_file_buffer, 'w') as zipper:
            for root, dirs, files in os.walk(folder_to_zip):
                LOGGER.info(root, dirs, files)
                self._write_files_in_buffer(zipper, root, files)

        self._delete_folder_for_downloaded_files(folder_to_zip)

        return zip_file_buffer.getvalue()

    @classmethod
    def _write_files_in_buffer(cls, zipper, root, files):
        for file in files:
            zipper.write(os.path.join(root, file))

    @classmethod
    def _delete_folder_for_downloaded_files(cls, folder_path):
        shutil.rmtree(folder_path)

    @classmethod
    def _generate_response_body(cls, response_data):
        return response_data

    @classmethod
    def _generate_headers(cls, entity_id):
        return {
            'Content-Type': 'application/zip',
            'Content-Disposition': f'attachment; filename={entity_id}_documents.zip'
        }


@add_schema(unknowns=True)
@dataclass
# pylint: disable=too-many-instance-attributes
class AMAProfilePDFEndpointParameters:
    path: dict
    query: dict
    authorization: dict
    database_name: str
    database_backend: str
    database_host: str
    database_port: str
    database_username: str
    database_password: str
    client_id: str
    client_secret: str
    client_env: str
    unknowns: dict = None


class AMAProfilePDFEndpointTask(APIEndpointTask, HttpClient):
    PARAMETER_CLASS = AMAProfilePDFEndpointParameters

    def run(self):
        self._set_parameter_defaults()
        LOGGER.debug('Parameters in AMAProfilePDFEndpointTask: %s', self._parameters)

        entity_id = self._parameters.path['entityId']

        access_token = self._get_ama_access_token()
        self._parameters.profile_headers['Authorization'] = f'Bearer {access_token}'

        self._check_if_profile_exists(entity_id)

        pdf_response = self._get_profile_pdf(entity_id)

        self._response_body = self._generate_response_body(pdf_response)
        self._headers = self._generate_headers(pdf_response)

    def _set_parameter_defaults(self):
        self._parameters.profile_headers = {
            'X-Location': 'Sample Vericre',
            'X-CredentialProviderUserId': "1",
            'X-SourceSystem': "1"
        }

    @classmethod
    def _generate_response_body(cls, response):
        return response.data

    @classmethod
    def _generate_headers(cls, response):
        return {
            'Content-Type': response.headers['Content-Type'],
            'Content-Disposition': response.headers['Content-Disposition']
        }

    def _get_ama_access_token(self):
        token_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        token_fields = {
            "grant_type": "client_credentials",
            "client_id": self._parameters.client_id,
            "client_secret": self._parameters.client_secret
        }

        token_body = urllib.parse.urlencode(token_fields)

        token_response = self.HTTP.request(
            'POST',
            f'https://{self._parameters.client_env}.ama-assn.org/oauth2/endpoint/eprofilesprovider/token',
            headers=token_headers,
            body=token_body
        )

        if token_response.status != 200:
            raise InternalServerError(
                f'Internal Server error caused by: {token_response.data}, status: {token_response.status}'
            )

        token_json = json.loads(token_response.data.decode("utf-8"))

        return token_json['access_token']

    def _check_if_profile_exists(self, entity_id):
        profile_response = self.HTTP.request(
            'GET',
            f'https://{self._parameters.client_env}.ama-assn.org/profiles/profile/full/{entity_id}',
            headers=self._parameters.profile_headers
        )

        if profile_response.status != 200:
            raise InternalServerError(
                f'Internal Server error caused by: {profile_response.reason}, status: {profile_response.status}'
            )

    def _get_profile_pdf(self, entity_id):
        pdf_resoponse = self.HTTP.request(
            'GET',
            f'https://{self._parameters.client_env}.ama-assn.org/profiles/pdf/full/{entity_id}',
            headers=self._parameters.profile_headers
        )

        if pdf_resoponse.status != 200:
            raise InternalServerError(
                f'Internal Server error caused by: {pdf_resoponse.reason}, status: {pdf_resoponse.status}'
            )

        return pdf_resoponse


@add_schema(unknowns=True)
@dataclass
# pylint: disable=too-many-instance-attributes
class CAQHProfilePDFEndpointParameters:
    path: dict
    query: dict
    authorization: dict
    database_name: str
    database_backend: str
    database_host: str
    database_port: str
    database_username: str
    database_password: str
    username: str
    password: str
    org_id: str
    application_type: str
    domain: str
    provider_api: str
    status_check_api: str
    unknowns: dict = None


class CAQHProfilePDFEndpointTask(APIEndpointTask, HttpClient):
    PARAMETER_CLASS = CAQHProfilePDFEndpointParameters

    def run(self):
        self._set_parameter_defaults()
        LOGGER.debug('Parameters: %s', self._parameters)

        with Database.from_parameters(self._parameters) as database:
            self._run(database)

    def _run(self, database):
        query = self._query_for_provider_id(database)

        query = self._filter(query)

        query_result = [row._asdict() for row in query.all()]

        self._verify_query_result(query_result)

        provider = query_result[0]['caqh_profile_id']

        pdf_response = self._fetch_caqh_pdf(provider)

        self._response_body = self._generate_response_body(pdf_response)
        self._headers = self._generate_headers(pdf_response)

    @classmethod
    def _query_for_provider_id(cls, database):
        return database.query(Physician.caqh_profile_id).join(User, User.id == Physician.user)

    def _filter(self, query):
        entity_id = self._parameters.path['entityId']
        query = self._filter_by_entity_id(query, entity_id)
        query = self._filter_by_active_user(query)

        return query

    @classmethod
    def _filter_by_entity_id(cls, query, entity_id):
        # temporary entity_id as ama_me_number
        return query.filter(User.ama_me_number == entity_id)

    @classmethod
    def _filter_by_active_user(cls, query):
        return query.filter(User.is_deleted == 'False').filter(User.status == 'ACTIVE')

    @classmethod
    def _verify_query_result(cls, query_result):
        exception = None
        if len(query_result) == 0:
            exception = ResourceNotFound("Provider ID from Entity ID in Vericre not found")
        elif len(query_result) > 1:
            exception = InternalServerError("Multiple records found for the given Entity ID in Vericre")

        if exception:
            raise exception

    def _set_parameter_defaults(self):
        self._parameters.auth_headers = urllib3.make_headers(
            basic_auth=f'{self._parameters.username}:{self._parameters.password}'
        )

    @classmethod
    def _generate_response_body(cls, response):
        return response.data

    @classmethod
    def _generate_headers(cls, response):
        return {
            'Content-Type': response.headers['Content-Type'],
            'Content-Disposition': response.headers['Content-Disposition']
        }

    def _fetch_caqh_pdf(self, provider):
        provider_id = self._get_caqh_provider_id(provider)

        parameters = urllib.parse.urlencode(
            {
                "applicationType": self._parameters.application_type,
                "docURL": "replica",
                "organizationId": self._parameters.org_id,
                "caqhProviderId": provider_id,
            }
        )

        response = self.HTTP.request(
            'GET',
            f'{self._parameters.domain}/{self._parameters.provider_api}?{parameters}',
            headers=self._parameters.auth_headers
        )

        if response.status != 200:
            raise InternalServerError(
                f'Internal Server error caused by: {response.data}, status: {response.status}'
            )

        return response

    def _get_caqh_provider_id(self, provider):
        provider_data = provider.split("-")
        provider_prefix = provider_data[0]
        provider_id = provider_data[1]

        caqh_provider_id = None

        if provider_prefix == 'caqh':
            caqh_provider_id = provider_id
        elif provider_prefix == 'npi':
            caqh_provider_id = self._get_caqh_provider_id_from_npi(provider_id)

        return caqh_provider_id

    def _get_caqh_provider_id_from_npi(self, npi):
        parameters = urllib.parse.urlencode(
            {
                "Product": "PV",
                "Organization_Id": self._parameters.org_id,
                "NPI_Provider_Id": npi,
            }
        )

        response = self.HTTP.request(
            'GET',
            f'{self._parameters.domain}/{self._parameters.status_check_api}?{parameters}',
            headers=self._parameters.auth_headers
        )

        if response.status != 200:
            raise InternalServerError(
                f'Internal Server error caused by: {response.data}, status: {response.status}'
            )

        provider_data = json.loads(response.data)

        if provider_data['provider_found_flag'] != "Y":
            raise ResourceNotFound(
                'CAQH Provider ID from NPI ID in CAQH ProView not found'
            )

        return provider_data['caqh_provider_id']
