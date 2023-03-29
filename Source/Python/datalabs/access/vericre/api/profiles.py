""" Release endpoint classes."""
from   dataclasses import dataclass
import logging

import boto3
# from   botocore.exceptions import ClientError
from sqlalchemy import func, literal, Integer

from   datalabs.access.api.task import APIEndpointTask
from   datalabs.access.orm import Database
from   datalabs.model.vericre.api import User, FormField, Document, Physician, Form, FormSection, FormSubSection
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=too-many-instance-attributes
@add_schema(unknowns=True)
@dataclass
class ProfilesEndpointParameters:
    path: dict
    query: dict
    authorization: dict
    database_name: str
    database_backend: str
    database_host: str
    database_port: str
    database_username: str
    database_password: str
    unknowns: dict=None


class ProfilesEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = ProfilesEndpointParameters

    def __init__(self, parameters: dict, data: "list<bytes>"=None):
        super().__init__(parameters, data)

        self._s3 = boto3.client('s3')

    def run(self):
        LOGGER.debug('Parameters: %s', self._parameters)

        with Database.from_parameters(self._parameters) as database:
            self._run(database)

        # self._response_body = self._generate_response_body("body-profile")

    def _run(self, database):
        self._set_parameter_defaults()

        sub_query = self._sub_query_for_documents(database)

        sub_query = self._filter(sub_query)

        query = self._query_for_documents(database, sub_query)

        query_result = query.all()

        response_result = [ row._asdict() for row in query_result]

        response_output = {"result": response_result}

        self._response_body = self._generate_response_body(response_output)

    def _set_parameter_defaults(self):
        pass


    @classmethod
    def _sub_query_for_documents(cls, database):
        return database.query(
                User.id.label('user_id'),
                FormField.name.label('field_name'),
                User.avatar_image,
                Document.document_name,
                Document.document_path
            ).join(Physician, User.id == Physician.user
            ).join(Form, Form.id == Physician.form
            ).join(FormSection, FormSection.form == Form.id
            ).join(FormSubSection, FormSubSection.form_section == FormSection.id
            ).join(FormField, FormField.form_sub_section == FormSubSection.id)

    @classmethod
    def _query_for_documents(cls, database, sub_query):
        # Define the subquery to get the required data
        docs_subquery = (sub_query.subquery())

        # Define the main query using the subquery
        docs_query = (
            database.query(
                docs_subquery.columns.field_name.label('document_identifier'),
                docs_subquery.columns.document_name,
                func.concat(docs_subquery.columns.user_id, '/', docs_subquery.columns.document_path).label('document_path')
            )
            .union(
                database.query(
                    literal('Profile Avatar').label('document_identifier'),
                    docs_subquery.columns.avatar_image,
                    func.concat(docs_subquery.columns.user_id, '/', 'Avatar').label('document_path')
                )
            )
        )
        return docs_query
    
    def _filter(self, query):
        me_number = self._parameters.query.get('meNumber')[0]
        LOGGER.info(f"me_number: {me_number}, {type(me_number)}")
        query = self._filter_by_me_number(query, me_number)

        return query.filter(FormField.type == 'FILE').filter(Document.is_deleted == False)

    @classmethod
    def _filter_by_me_number(cls, query, me_number):
        return query.filter(User.ama_me_number == me_number)
    
    @classmethod
    def _generate_response_body(cls, msg):
        return msg
