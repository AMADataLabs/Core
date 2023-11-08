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
import urllib3

from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound, InternalServerError
from   datalabs.access.aws import AWSClient
from   datalabs.access.orm import Database
from   datalabs.access.vericre.api.authentication import PassportAuthenticatingEndpointMixin
from   datalabs.model.vericre.api import APILedger
from   datalabs.parameter import add_schema
from   datalabs.util.profile import run_time_logger

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
    document_bucket: str
    document_key: str
    request_ip: str
    document_version_id: str = ''


class CommonEndpointUtilities:
    @classmethod
    @run_time_logger
    def save_audit_log(cls, database, document_data, audit_log_parameters):
        document_bucket = audit_log_parameters.document_bucket
        document_key = audit_log_parameters.document_key

        audit_log_parameters.document_version_id = cls._upload_document_onto_s3(
            document_bucket,
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
    @run_time_logger
    def _upload_document_onto_s3(cls, document_bucket, document_key, data):
        version_id = ''

        try:
            md5_hash = base64.b64encode(hashlib.md5(data).digest())

            with AWSClient('s3') as aws_s3:
                put_object_result = aws_s3.put_object(
                    Bucket=document_bucket,
                    Key=document_key,
                    Body=data,
                    ContentMD5=md5_hash.decode()
                )

                version_id = cls._process_put_object_result(put_object_result)
        except ClientError as error:
            LOGGER.exception(error.response)
            raise InternalServerError("An error occurred when saving a file to S3") from error

        return version_id

    @classmethod
    def _process_put_object_result(cls, put_object_result):
        if put_object_result["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise InternalServerError("An error occurred when saving a file to S3")

        return put_object_result["VersionId"]

    @classmethod
    @run_time_logger
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
    document_bucket: str
    unknowns: dict = None


class ProfileDocumentsEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = ProfileDocumentsEndpointParameters

    def run(self):
        LOGGER.debug('Parameters in ProfileDocumentsEndpointTask: %s', self._parameters)

        with Database.from_parameters(self._parameters) as database:
            self._run(database)

    def _run(self, database):
        entity_id = self._parameters.path['entity_id']
        source_ip = self._parameters.identity['sourceIp']

        sql = self._query_for_documents(entity_id)

        query = self._execute_sql(database, sql)

        query_result = self._convert_query_result_to_list(query)

        self._download_files_for_profile(query_result, entity_id)

        zip_file_in_bytes = self._zip_downloaded_files(entity_id)

        current_date_time = CommonEndpointUtilities.get_current_datetime()

        audit_parameters = AuditLogParameters(
            entity_id=entity_id,
            request_type=StaticTaskParameters.REQUEST_TYPE["Documents"],
            authorization=self._parameters.authorization,
            document_bucket=self._parameters.document_bucket,
            document_key=f'downloaded_documents/Documents/{entity_id}_documents_{current_date_time}.zip',
            request_ip=source_ip
        )

        CommonEndpointUtilities.save_audit_log(database, zip_file_in_bytes, audit_parameters)

        self._generate_response(zip_file_in_bytes, entity_id, current_date_time)

    @classmethod
    def _query_for_documents(cls, entity_id):
        sql = f'''
            with docs as
            (
                select
                    u.id as user_id,
                    ff."name" as field_name,
                    u.avatar_image,
                    d.document_name,
                    d.document_path
                from "user" u
                join physician p on u.id = p."user"
                    and u.ama_entity_id = '{entity_id}'
                    and u.is_deleted = false
                    and u.status = 'ACTIVE'
                join form_field ff on ff.form = p.form
                    and ff."type" = 'FILE'
                    and ff.sub_section is not null
                join "document" d on d.id = cast(ff."values" ->>0 as INT)
                    and d.is_deleted = false
            )
            select
                field_name as document_identifier,document_name,concat (user_id,'/',document_path) as document_path
            from docs
            union
            select
                'Profile Avatar',avatar_image,concat(user_id ,'/','Avatar') as document_path from docs
        '''

        return sql

    @classmethod
    @run_time_logger
    def _execute_sql(cls, database, sql):
        query = database.execute(sql)
        return query

    @classmethod
    @run_time_logger
    def _convert_query_result_to_list(cls, query):
        query_result = [dict(row) for row in query.fetchall()]
        return query_result

    def _download_files_for_profile(self, query_result, entity_id):
        if len(query_result) == 0:
            raise ResourceNotFound('No documents where found in VeriCre for the given entity ID.')

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
        download_file_name = document_name if file['document_identifier'] != 'Profile Avatar' \
            else f'Avatar.{document_name.split(".")[-1]}'

        try:
            with AWSClient('s3') as aws_s3:
                aws_s3.download_file(
                    Bucket=self._parameters.document_bucket,
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
