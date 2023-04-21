""" Release endpoint classes."""
from dataclasses import dataclass
import io
import json
import logging
import os
import shutil
import urllib3
import urllib.parse

from botocore.exceptions import ClientError
from sqlalchemy import func, literal, Integer
import zipfile

from datalabs.access.api.task import APIEndpointTask, ResourceNotFound, InternalServerError, InvalidRequest
from datalabs.access.aws import AWSClient
from datalabs.access.orm import Database
from datalabs.model.vericre.api import User, FormField, Document, Physician, Form, FormSection, FormSubSection
from datalabs.parameter import add_schema

HTTP = urllib3.PoolManager()
logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema(unknowns=True)
@dataclass
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


class ProfileDocumentsEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = ProfileDocumentsEndpointParameters

    def run(self):
        LOGGER.debug(
            'Parameters in ProfileDocumentsEndpointTask: %s', self._parameters)

        with Database.from_parameters(self._parameters) as database:
            self._run(database)

    def _run(self, database):
        entity_id = self._parameters.path.get('entityId')

        sub_query = self._sub_query_for_documents(database)

        sub_query = self._filter(sub_query, entity_id)

        query = self._query_for_documents(database, sub_query)

        query_result = [row._asdict() for row in query.all()]

        self._download_files(query_result, entity_id)

        zip_file_in_bytes = self._zip_downloaded_files(entity_id)

        self._response_body = self._generate_response_body(zip_file_in_bytes)
        self._headers = self._generate_headers(entity_id)

    def _sub_query_for_documents(self, database):
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

        return query.filter(FormField.type == 'FILE').filter(Document.is_deleted == False)

    def _filter_by_entity_id(self, query, entity_id):
        # query me_number temporary and will update to filter by ama_entity_id in next sprint
        return query.filter(User.ama_me_number == entity_id)

    def _query_for_documents(self, database, sub_query):
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

    def _download_files(self, query_result, entity_id):
        if len(query_result) == 0:
            raise ResourceNotFound('No file found for the given entity ID')

        os.mkdir(f'./{entity_id}')

        for item in query_result:
            with AWSClient('s3') as s3:
                encoded_document_name = urllib.parse.quote(
                    item['document_name'],
                    safe=' '
                ).replace(" ", "+")

                document_key = f"{item['document_path']}/{encoded_document_name}"

                self._get_files(s3, entity_id, document_key,
                                item['document_name'])

    def _get_files(self, s3, entity_id, key, filename):
        try:
            s3.download_file(
                Bucket=self._parameters.document_bucket_name,
                Key=key,
                Filename=f"{entity_id}/{filename}"
            )
            LOGGER.info(f"{entity_id}/{filename} downloaded.")

        except ClientError as error:
            LOGGER.error(error.response)

    def _zip_downloaded_files(self, entity_id):
        dir_to_zip = f'./{entity_id}'
        zip_file_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_file_buffer, 'w') as zip:
            for root, dirs, files in os.walk(dir_to_zip):
                for file in files:
                    zip.write(os.path.join(root, file))

        zip_file_bytes = zip_file_buffer.getvalue()

        # Delete downloaded files
        shutil.rmtree(dir_to_zip)

        return zip_file_bytes

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


class AMAProfilePDFEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = AMAProfilePDFEndpointParameters

    def run(self):
        self._set_parameter_defaults()
        LOGGER.debug('Parameters in AMAProfilePDFEndpointTask: %s',
                     self._parameters)

        entity_id = self._parameters.path['entityId']

        access_token = self.get_ama_access_token()
        self._parameters.profile_headers['Authorization'] = f'Bearer {access_token}'

        self.check_if_profile_exists(entity_id)

        pdf_response = self.get_profile_pdf(entity_id)

        self._response_body = self._generate_response_body(pdf_response)
        self._headers = self._generate_headers(pdf_response)

    def _set_parameter_defaults(self):
        self._parameters.profile_headers = {
            'X-Location': 'Sample Vericre',
            'X-CredentialProviderUserId': "1",
            'X-SourceSystem': "1"
        }

    def _generate_response_body(self, response):
        return response.data

    def _generate_headers(self, response):
        return {
            'Content-Type': response.headers['Content-Type'],
            'Content-Disposition': response.headers['Content-Disposition']
        }

    def get_ama_access_token(self):
        token_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        token_fields = {
            "grant_type": "client_credentials",
            "client_id": self._parameters.client_id,
            "client_secret": self._parameters.client_secret
        }

        token_body = urllib.parse.urlencode(token_fields)

        token_response = HTTP.request(
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

    def check_if_profile_exists(self, entity_id):
        profile_response = HTTP.request(
            'GET',
            f'https://{self._parameters.client_env}.ama-assn.org/profiles/profile/full/{entity_id}',
            headers=self._parameters.profile_headers
        )

        if profile_response.status != 200:
            raise InternalServerError(
                f'Internal Server error caused by: {profile_response.reason}, status: {profile_response.status}'
            )

    def get_profile_pdf(self, entity_id):

        pdf_resoponse = HTTP.request(
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


class CAQHProfilePDFEndpointTask(APIEndpointTask):
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

        if len(query_result) == 0:
            raise ResourceNotFound(
                "Provider Id from Entity Id in Vericre not found"
            )

        elif len(query_result) > 1:
            raise InternalServerError(
                "Multiple records found for the given Entity Id in Vericre"
            )

        provider = query_result[0]['caqh_profile_id']

        provider_data = provider.split("-")
        provider_prefix = provider_data[0]
        provider_id = provider_data[1]

        if provider_prefix == 'caqh':
            caqh_provider_id = provider_id

        elif provider_prefix == 'npi':
            caqh_provider_id = self.get_caqh_provider_id_from_npi(provider_id)

        else:
            caqh_provider_id = None

        pdf_response = self.fetch_caqh_pdf(caqh_provider_id)

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
        # TODO change here
        return query.filter(User.ama_me_number == entity_id)

    @classmethod
    def _filter_by_active_user(cls, query):
        return query.filter(User.is_deleted == False).filter(User.status == 'ACTIVE')

    def generate_pdf(self, response):
        path = os.path.join(os.path.expanduser(
            '~'), 'Documents/CAQH', self._parameters.path['entityId'] + ".pdf")
        with open(path, "wb") as outfile:
            outfile.write(response.data)

    def _set_parameter_defaults(self):
        self._parameters.auth_headers = urllib3.make_headers(
            basic_auth=f'{self._parameters.username}:{self._parameters.password}')

    def _generate_response_body(self, response):
        return response.data

    def _generate_headers(self, response):
        return {
            'Content-Type': response.headers['Content-Type'],
            'Content-Disposition': response.headers['Content-Disposition']
        }

    def fetch_caqh_pdf(self, provider_id):
        parameters = urllib.parse.urlencode(
            {
                "applicationType": self._parameters.application_type,
                "docURL": "replica",
                "organizationId": self._parameters.org_id,
                "caqhProviderId": provider_id,
            }
        )

        response = HTTP.request(
            'GET',
            f'{self._parameters.domain}/{self._parameters.provider_api}?{parameters}',
            headers=self._parameters.auth_headers
        )

        if response.status != 200:
            raise InternalServerError(
                f'Internal Server error caused by: {response.data}, status: {response.status}'
            )

        return response

    def get_caqh_provider_id_from_npi(self, npi):
        parameters = urllib.parse.urlencode(
            {
                "Product": "PV",
                "Organization_Id": self._parameters.org_id,
                "NPI_Provider_Id": npi,
            }
        )

        response = HTTP.request(
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
                'CAQH Provider Id from NPI Id in CAQH ProView not found'
            )

        return provider_data['caqh_provider_id']
