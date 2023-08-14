""" Release endpoint classes."""
import base64
import cgi
from   dataclasses import dataclass
from   datetime import datetime
import hashlib
import io
import json
import logging
import os
import shutil
import time
import urllib.parse
import zipfile

from   botocore.exceptions import ClientError
from   sqlalchemy import func, literal, Integer
import urllib3

from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound, InternalServerError
from   datalabs.access.aws import AWSClient
from   datalabs.access.orm import Database
from   datalabs.model.vericre.api \
    import APILedger, Document, Form, FormField, FormSection, FormSubSection, Physician, User
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class HttpClient:
    HTTP = urllib3.PoolManager()

class StaticTaskParameters:
    DOCUMENT_TEMP_DIRECTORY = '/tmp/vericre_api_documents'
    USER_PHYSICIAN = 'physician'
    REQUEST_TYPE = {"Documents": "Documents", "AMA": "ama_profile_pdf", "CAQH": "caqh_profile_pdf"}
    PROFILE_HEADERS = {
        'X-Location': 'Sample Vericre',
        'X-CredentialProviderUserId': "1",
        'X-SourceSystem': "1"
    }


@dataclass
class AuditLogParameters:
    entity_id: str
    request_type: str
    authorization: dict
    document_bucket_name: str
    document_key: str
    request_ip: str
    document_version_id: str = ''


class CommonEndpointUtilities:
    @classmethod
    def save_audit_log(cls, database, document_data, audit_log_parameters):
        document_bucket_name = audit_log_parameters.document_bucket_name
        document_key = audit_log_parameters.document_key

        audit_log_parameters.document_version_id = cls._upload_document_onto_s3(
            document_bucket_name,
            document_key,
            document_data
        )

        cls._add_audit_log_record_in_db(database, audit_log_parameters, StaticTaskParameters.USER_PHYSICIAN)

    @classmethod
    def _get_client_info_from_authorization(cls, authorization):
        customer_id = authorization['user_id']
        customer_name = authorization['user_name']

        return customer_id, customer_name

    @classmethod
    def _upload_document_onto_s3(cls, document_bucket_name, document_key, data):
        version_id = ''

        try:
            md5_hash = base64.b64encode(hashlib.md5(data).digest())

            with AWSClient('s3') as aws_s3:
                put_object_result = aws_s3.put_object(
                    Bucket=document_bucket_name,
                    Key=document_key,
                    Body=data,
                    ContentMD5=md5_hash.decode()
                )

                version_id = cls._process_put_object_result(put_object_result)
        except ClientError as error:
            LOGGER.exception(error.response)
            raise InternalServerError("Error occurred in saving file in S3") from error

        return version_id

    @classmethod
    def _process_put_object_result(cls, put_object_result):
        if put_object_result["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise InternalServerError("Error occurred in saving file in S3")

        return put_object_result["VersionId"]

    @classmethod
    def _add_audit_log_record_in_db(cls, database, audit_log_parameters, user_type):
        entity_id = audit_log_parameters.entity_id
        request_type = audit_log_parameters.request_type
        authorization = audit_log_parameters.authorization
        file_path = audit_log_parameters.document_key
        document_version_id = audit_log_parameters.document_version_id
        request_ip = audit_log_parameters.request_ip

        customer_id, customer_name = cls._get_client_info_from_authorization(authorization)

        new_record = APILedger(
            created_at = int(time.time()),
            customer_id = customer_id,
            customer_name = customer_name,
            document_version_id = document_version_id,
            entity_id = entity_id,
            file_path = file_path,
            request_date = str(int(time.time())),
            request_ip = request_ip,
            request_type = request_type,
            user_type = user_type
        )

        database.add(new_record)
        database.commit()

    @classmethod
    def get_current_datetime(cls):
        current_date_time = datetime.now()
        current_date_time_str = current_date_time.strftime("%Y%m%d%H%M%S")

        return current_date_time_str


@add_schema(unknowns=True)
@dataclass
# pylint: disable=too-many-instance-attributes
class ProfileDocumentsEndpointParameters:
    path: dict
    query: dict
    authorization: dict
    identity: dict
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
        LOGGER.debug('Parameters in ProfileDocumentsEndpointTask: %s', self._parameters)

        with Database.from_parameters(self._parameters) as database:
            self._run(database)

    def _run(self, database):
        entity_id = self._parameters.path['entityId']
        source_ip = self._parameters.identity['sourceIp']

        sub_query = self._sub_query_for_documents(database)

        sub_query = self._filter(sub_query, entity_id)

        query = self._query_for_documents(database, sub_query)

        query_result = [row._asdict() for row in query.all()]

        self._download_files_for_profile(query_result, entity_id)

        zip_file_in_bytes = self._zip_downloaded_files(entity_id)

        current_date_time = CommonEndpointUtilities.get_current_datetime()

        audit_parameters = AuditLogParameters(
            entity_id=entity_id,
            request_type=StaticTaskParameters.REQUEST_TYPE["Documents"],
            authorization=self._parameters.authorization,
            document_bucket_name=self._parameters.document_bucket_name,
            document_key=f'downloaded_documents/Documents/{entity_id}_documents_{current_date_time}.zip',
            request_ip=source_ip
        )

        CommonEndpointUtilities.save_audit_log(database, zip_file_in_bytes, audit_parameters)

        self._generate_response(zip_file_in_bytes, entity_id, current_date_time)

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
        query = self._filter_by_active_user(query)

        return query.filter(FormField.type == 'FILE').filter(Document.is_deleted == 'False')

    @classmethod
    def _filter_by_entity_id(cls, query, entity_id):
        return query.filter(User.ama_entity_id == entity_id)

    @classmethod
    def _filter_by_active_user(cls, query):
        return query.filter(User.is_deleted == 'False').filter(User.status == 'ACTIVE')

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
            raise ResourceNotFound('Document for the given entity ID is not found in VeriCre.')

        self._create_folder_for_downloaded_files(entity_id)

        for file in query_result:
            self._verify_and_get_files_from_s3(entity_id, file)

    @classmethod
    def _create_folder_for_downloaded_files(cls, entity_id):
        os.makedirs(f'{StaticTaskParameters.DOCUMENT_TEMP_DIRECTORY}/{entity_id}')

    def _verify_and_get_files_from_s3(self, entity_id, file):
        if not isinstance(file['document_name'], type(None)):
            self._get_files_from_s3(entity_id, file)

    def _get_files_from_s3(self, entity_id, file):
        document_name = file['document_name']
        encoded_document_name = self._encode_document_name(file)
        document_key = f"{file['document_path']}/{encoded_document_name}"
        download_file_name = document_name if file['document_identifier'] != 'Profile Avatar' else 'Avatar'

        try:
            with AWSClient('s3') as aws_s3:
                aws_s3.download_file(
                    Bucket=self._parameters.document_bucket_name,
                    Key=document_key,
                    Filename=f"{StaticTaskParameters.DOCUMENT_TEMP_DIRECTORY}/{entity_id}/{download_file_name}"
                )

                LOGGER.info("%s/%s downloaded.", entity_id, download_file_name)
        except ClientError as error:
            LOGGER.error("document_name: %s", document_name)
            LOGGER.error("document_key: %s", document_key)
            LOGGER.exception(error.response)

    @classmethod
    def _encode_document_name(cls, file):
        encoded_document_name = file['document_name']

        if file['document_identifier'] != 'Profile Avatar':
            encoded_document_name = urllib.parse.quote(
                file['document_name'],
                safe=' '
            ).replace(" ", "+")

        return encoded_document_name

    def _zip_downloaded_files(self, entity_id):
        folder_to_zip = f'{StaticTaskParameters.DOCUMENT_TEMP_DIRECTORY}/{entity_id}'
        zip_file_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_file_buffer, 'w') as zipper:
            for root, dirs, files in os.walk(folder_to_zip):
                LOGGER.info("root: %s, dir length: %s, files size: %s", root, len(dirs), len(files))
                self._write_files_in_buffer(zipper, root, files)

        self._delete_folder_for_downloaded_files(folder_to_zip)

        return zip_file_buffer.getvalue()

    @classmethod
    def _write_files_in_buffer(cls, zipper, root, files):
        for file in files:
            zipper.write(os.path.join(root, file), arcname=file)

    @classmethod
    def _delete_folder_for_downloaded_files(cls, folder_path):
        shutil.rmtree(folder_path)

    def _generate_response(self, zip_file_in_bytes, entity_id, current_date_time):
        self._response_body = self._generate_response_body(zip_file_in_bytes)
        self._headers = self._generate_headers(entity_id, current_date_time)

    @classmethod
    def _generate_response_body(cls, response_data):
        return response_data

    @classmethod
    def _generate_headers(cls, entity_id, current_date_time):
        return {
            'Content-Type': 'application/zip',
            'Content-Disposition': f'attachment; filename={entity_id}_documents_{current_date_time}.zip'
        }


@add_schema(unknowns=True)
@dataclass
# pylint: disable=too-many-instance-attributes
class AMAProfilePDFEndpointParameters:
    path: dict
    query: dict
    authorization: dict
    identity: dict
    database_name: str
    database_backend: str
    database_host: str
    database_port: str
    database_username: str
    database_password: str
    document_bucket_name: str
    client_id: str
    client_secret: str
    client_env: str
    unknowns: dict = None


class AMAProfilePDFEndpointTask(APIEndpointTask, HttpClient):
    PARAMETER_CLASS = AMAProfilePDFEndpointParameters

    def run(self):
        LOGGER.debug('Parameters in AMAProfilePDFEndpointTask: %s', self._parameters)

        with Database.from_parameters(self._parameters) as database:
            self._run(database)

    def _run(self, database):
        entity_id = self._parameters.path['entityId']
        source_ip = self._parameters.identity['sourceIp']

        access_token = self._get_ama_access_token()
        StaticTaskParameters.PROFILE_HEADERS['Authorization'] = f'Bearer {access_token}'

        self._assert_profile_exists(entity_id)

        pdf_response = self._get_profile_pdf(entity_id)

        pdf_filename = cgi.parse_header(pdf_response.headers['Content-Disposition'])[1]["filename"]

        audit_parameters = AuditLogParameters(
            entity_id=entity_id,
            request_type=StaticTaskParameters.REQUEST_TYPE["AMA"],
            authorization=self._parameters.authorization,
            document_bucket_name=self._parameters.document_bucket_name,
            document_key=f'downloaded_documents/AMA_Profile_PDF/{pdf_filename}',
            request_ip=source_ip
        )

        CommonEndpointUtilities.save_audit_log(database, pdf_response.data, audit_parameters)

        self._generate_response(pdf_response)

    def _generate_response(self, response):
        self._response_body = self._generate_response_body(response)
        self._headers = self._generate_headers(response)

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

        token_response = self._request_ama_token(token_headers, token_body)

        if token_response.status != 200:
            raise InternalServerError(
                f'Internal Server error caused by: {token_response.data}, status: {token_response.status}'
            )

        token_json = json.loads(token_response.data.decode("utf-8"))

        return token_json['access_token']

    def _request_ama_token(self, token_headers, token_body):
        return self.HTTP.request(
            'POST',
            f'https://{self._parameters.client_env}.ama-assn.org/oauth2/endpoint/eprofilesprovider/token',
            headers=token_headers,
            body=token_body
        )

    def _assert_profile_exists(self, entity_id):
        profile_response = self._request_ama_profile(entity_id)

        if profile_response.status != 200:
            raise InternalServerError(
                f'Internal Server error caused by: {profile_response.reason}, status: {profile_response.status}'
            )

    def _request_ama_profile(self, entity_id):
        return self.HTTP.request(
            'GET',
            f'https://{self._parameters.client_env}.ama-assn.org/profiles/profile/full/{entity_id}',
            headers=StaticTaskParameters.PROFILE_HEADERS
        )

    def _get_profile_pdf(self, entity_id):
        pdf_resoponse = self._request_ama_profile_pdf(entity_id)

        if pdf_resoponse.status != 200:
            raise InternalServerError(
                f'Internal Server error caused by: {pdf_resoponse.reason}, status: {pdf_resoponse.status}'
            )

        return pdf_resoponse

    def _request_ama_profile_pdf(self, entity_id):
        return self.HTTP.request(
            'GET',
            f'https://{self._parameters.client_env}.ama-assn.org/profiles/pdf/full/{entity_id}',
            headers=StaticTaskParameters.PROFILE_HEADERS
        )


@add_schema(unknowns=True)
@dataclass
# pylint: disable=too-many-instance-attributes
class CAQHProfilePDFEndpointParameters:
    path: dict
    query: dict
    authorization: dict
    identity: dict
    database_name: str
    database_backend: str
    database_host: str
    database_port: str
    database_username: str
    database_password: str
    document_bucket_name: str
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
        entity_id = self._parameters.path['entityId']
        source_ip = self._parameters.identity['sourceIp']

        query = self._query_for_provider_id(database)

        query = self._filter(query)

        query_result = [row._asdict() for row in query.all()]

        self._verify_query_result(query_result)

        provider = query_result[0]['caqh_profile_id']

        pdf_response = self._fetch_caqh_pdf(provider)

        pdf_filename = cgi.parse_header(pdf_response.headers['Content-Disposition'])[1]["filename"]

        current_date_time = CommonEndpointUtilities.get_current_datetime()

        audit_parameters = AuditLogParameters(
            entity_id=entity_id,
            request_type=StaticTaskParameters.REQUEST_TYPE["CAQH"],
            authorization=self._parameters.authorization,
            document_bucket_name=self._parameters.document_bucket_name,
            document_key= \
                f'downloaded_documents/CAQH_Profile_PDF/{pdf_filename.replace(".pdf", f"_{current_date_time}.pdf")}',
            request_ip=source_ip
        )

        CommonEndpointUtilities.save_audit_log(database, pdf_response.data, audit_parameters)

        self._generate_response(pdf_response, current_date_time)

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
        return query.filter(User.ama_entity_id == entity_id)

    @classmethod
    def _filter_by_active_user(cls, query):
        return query.filter(User.is_deleted == 'False').filter(User.status == 'ACTIVE')

    @classmethod
    def _verify_query_result(cls, query_result):
        exception = None
        if len(query_result) == 0:
            exception = ResourceNotFound("Provider ID from the given entity ID is not found in VeriCre.")
        elif len(query_result) > 1:
            exception = InternalServerError("Multiple records found for the given Entity ID in VeriCre.")
        elif isinstance(query_result[0]['caqh_profile_id'], type(None)) or query_result[0]['caqh_profile_id'] == '':
            exception = ResourceNotFound("Provider ID from the given entity ID is not found in VeriCre.")

        if exception:
            raise exception

    def _set_parameter_defaults(self):
        self._parameters.authorization['auth_headers'] = urllib3.make_headers(
            basic_auth=f'{self._parameters.username}:{self._parameters.password}'
        )

    def _generate_response(self, response, current_date_time):
        self._response_body = self._generate_response_body(response)
        self._headers = self._generate_headers(response, current_date_time)

    @classmethod
    def _generate_response_body(cls, response):
        return response.data

    @classmethod
    def _generate_headers(cls, response, current_date_time):
        LOGGER.info("header type: %s", type(response.headers['Content-Disposition']))
        return {
            'Content-Type': response.headers['Content-Type'],
            'Content-Disposition': response.headers['Content-Disposition'].replace(".pdf", f"_{current_date_time}.pdf")
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

        response = self._request_caqh_pdf(parameters)

        if response.status != 200:
            raise InternalServerError(
                f'Internal Server error caused by: {response.data}, status: {response.status}'
            )

        return response

    def _request_caqh_pdf(self, parameters):
        return self.HTTP.request(
            'GET',
            f'{self._parameters.domain}/{self._parameters.provider_api}?{parameters}',
            headers=self._parameters.authorization['auth_headers']
        )

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

        response = self._request_caqh_provider_id_from_npi(parameters)

        if response.status != 200:
            raise InternalServerError(
                f'Internal Server error caused by: {response.data}, status: {response.status}'
            )

        provider_data = json.loads(response.data)

        if provider_data['provider_found_flag'] != "Y":
            raise ResourceNotFound(
                'CAQH Provider ID from the given NPI ID is not found in CAQH ProView.'
            )

        return provider_data['caqh_provider_id']

    def _request_caqh_provider_id_from_npi(self, parameters):
        return self.HTTP.request(
            'GET',
            f'{self._parameters.domain}/{self._parameters.status_check_api}?{parameters}',
            headers=self._parameters.authorization['auth_headers']
        )
    