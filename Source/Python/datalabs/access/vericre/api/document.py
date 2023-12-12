""" Release endpoint classes."""
from   dataclasses import dataclass
import io
import logging
import os
import shutil
import tempfile
from   typing import Optional
import urllib.parse
import zipfile

from botocore.exceptions import ClientError

from datalabs.access.api.task import APIEndpointTask, ResourceNotFound
from datalabs.access.aws import AWSClient
from datalabs.access.orm import Database
from datalabs.access.vericre.api.audit import AuditLogger, AuditLogParameters, RequestType
from datalabs.access.vericre.api.datetime import get_current_datetime
from datalabs.parameter import add_schema
from datalabs.util.profile import run_time_logger

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


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
    unknowns: Optional[dict] = None


class ProfileDocumentsEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = ProfileDocumentsEndpointParameters

    def run(self):
        LOGGER.debug("Parameters in ProfileDocumentsEndpointTask: %s", self._parameters)

        with Database.from_parameters(self._parameters) as database:
            self._run(database)

    def _run(self, database):
        entity_id = self._parameters.path["entity_id"]
        source_ip = self._parameters.identity["sourceIp"]

        sql = self._query_for_documents(entity_id)

        query = self._execute_sql(database, sql)

        query_result = self._convert_query_result_to_list(query)

        with tempfile.TemporaryDirectory(entity_id) as directory:
            self._download_files_for_profile(query_result, directory)

            zip_file_in_bytes = self._zip_downloaded_files(directory)

        current_date_time = get_current_datetime()

        audit_parameters = AuditLogParameters(
            entity_id=entity_id,
            request_type=RequestType.DOCUMENTS,
            authorization=self._parameters.authorization,
            document_bucket=self._parameters.document_bucket,
            document_key=f"downloaded_documents/Documents/{entity_id}_documents_{current_date_time}.zip",
            request_ip=source_ip,
        )

        AuditLogger.save_audit_log(database, zip_file_in_bytes, audit_parameters)

        self._generate_response(zip_file_in_bytes, entity_id, current_date_time)

    @classmethod
    def _query_for_documents(cls, entity_id):
        sql = f"""
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
        """

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

    def _download_files_for_profile(self, query_result, directory):
        if len(query_result) == 0:
            raise ResourceNotFound("No documents where found in VeriCre for the given entity ID.")

        for file in query_result:
            self._verify_and_get_files_from_s3(file, directory)

    def _zip_downloaded_files(self, directory):
        zip_file_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_file_buffer, "w") as zipper:
            for root, dirs, files in os.walk(directory):
                LOGGER.info("root: %s, dir length: %s, files size: %s", root, len(dirs), len(files))
                self._write_files_in_buffer(zipper, root, files)

        self._delete_folder_for_downloaded_files(directory)

        return zip_file_buffer.getvalue()

    def _generate_response(self, zip_file_in_bytes, entity_id, current_date_time):
        self._response_body = zip_file_in_bytes

        self._headers = {
            "Content-Type": "application/zip",
            "Content-Disposition": f"attachment; filename={entity_id}_documents_{current_date_time}.zip",
        }

    def _verify_and_get_files_from_s3(self, file, directory):
        if not isinstance(file["document_name"], type(None)):
            self._get_files_from_s3(file, directory)

    @classmethod
    def _write_files_in_buffer(cls, zipper, root, files):
        for file in files:
            zipper.write(os.path.join(root, file), arcname=file)

    @classmethod
    def _delete_folder_for_downloaded_files(cls, folder_path):
        shutil.rmtree(folder_path)

    def _get_files_from_s3(self, file, directory):
        document_name = file["document_name"]
        encoded_document_name = self._encode_document_name(file)
        document_key = f"{file['document_path']}/{encoded_document_name}"
        download_file_name = (
            document_name
            if file["document_identifier"] != "Profile Avatar"
            else f'Avatar.{document_name.split(".")[-1]}'
        )
        download_path = os.path.join(directory, download_file_name)

        try:
            with AWSClient("s3") as aws_s3:
                aws_s3.download_file(Bucket=self._parameters.document_bucket, Key=document_key, Filename=download_path)

                LOGGER.info("Downloaded %s.", download_path)
        except ClientError as error:
            LOGGER.error("document_name: %s", document_name)
            LOGGER.error("document_key: %s", document_key)
            LOGGER.exception(error.response)

    @classmethod
    def _encode_document_name(cls, file):
        encoded_document_name = file["document_name"]

        if file["document_identifier"] != "Profile Avatar":
            encoded_document_name = urllib.parse.quote(file["document_name"], safe=" ").replace(" ", "+")

        return encoded_document_name
