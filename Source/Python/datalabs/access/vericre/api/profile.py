""" Release endpoint classes."""
import base64
from   dataclasses import dataclass
import io
import json
import logging
import os
import shutil
import urllib.parse

from amazon.ion.json_encoder import IonToJSONEncoder
from botocore.exceptions import ClientError
from pyqldb.driver.qldb_driver import QldbDriver
from sqlalchemy import func, literal, Integer
import zipfile

from datalabs.access.api.task import APIEndpointTask, ResourceNotFound
from datalabs.access.aws import AWSClient
from datalabs.access.orm import Database
from datalabs.model.vericre.api import User, FormField, Document, Physician, Form, FormSection, FormSubSection
from datalabs.parameter import add_schema

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
    unknowns: dict=None


class BaseProfileEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = ProfileDocumentsEndpointParameters

    def run(self):
        LOGGER.debug('Parameters: %s', self._parameters)

        with Database.from_parameters(self._parameters) as database:
            self._run(database)

    def _run(self):
        pass

    @classmethod
    def _generate_response_body(cls, response_data):
        return response_data

    @classmethod
    def _generate_headers(cls, content_type, content_disposition):
        return {
            'Content-Type': content_type,
            'Content-Disposition': content_disposition
        }


class ProfileDocumentsEndpointTask(BaseProfileEndpointTask):

    def _run(self, database):
        entity_id = self._parameters.path.get('entityId')

        sub_query = self._sub_query_for_documents(database)

        sub_query = self._filter(sub_query, entity_id)

        query = self._query_for_documents(database, sub_query)

        query_result = [row._asdict() for row in query.all()]

        self._download_files(query_result, entity_id)

        zip_file_in_bytes = self._zip_downloaded_files(entity_id)

        self._response_body = self._generate_response_body(zip_file_in_bytes)
        self._headers = self._generate_headers(
            'application/zip', 
            f'attachment; filename={entity_id}_documents.zip'
        )

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
                func.concat(subquery.columns.user_id, '/', 'Avatar').label('document_path')
            )
        )

    def _download_files(self, query_result, entity_id):
        if len(query_result) == 0:
            raise ResourceNotFound('No file found for the given entity ID')
        
        os.mkdir(f'./{entity_id}')

        for item in query_result:
            with AWSClient('s3') as s3:
                encoded_document_name = urllib.parse.quote(item['document_name'], safe=' ').replace(" ", "+")
                document_key = f"{item['document_path']}/{encoded_document_name}"

                self._get_files(s3, entity_id, document_key, item['document_name'])

    def _get_files(self, s3, entity_id, key, filename):
        try:
            s3.download_file(Bucket=self._parameters.document_bucket_name, Key=key, Filename=f"{entity_id}/{filename}")
            LOGGER.info(f"{entity_id}/{filename} downloaded.")

        except ClientError as error:
            LOGGER.error(error.response)

    def _zip_downloaded_files(self, entity_id):
        dir_to_zip = f'./{entity_id}'
        buffer = io.BytesIO()

        with zipfile.ZipFile(buffer, 'w') as zip:
            for root, dirs, files in os.walk(dir_to_zip):
                for file in files:
                    zip.write(os.path.join(root, file))

        zip_file_bytes = buffer.getvalue()

        # Delete downloaded files
        shutil.rmtree(dir_to_zip)

        return zip_file_bytes


class AMAProfilePDFEndpointTask(BaseProfileEndpointTask):
    def _run(self, database):
        print("TODO")


class CAQHProfilePDFEndpointTask(BaseProfileEndpointTask):
    def _run(self, database):
        print("TODO")