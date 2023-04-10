""" Release endpoint classes."""
from   dataclasses import dataclass
import logging

from sqlalchemy import func, literal, Integer

from   datalabs.access.api.task import APIEndpointTask
from   datalabs.access.orm import Database
from   datalabs.model.vericre.api import User, FormField, Document, Physician, Form, FormSection, FormSubSection
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema(unknowns=True)
@dataclass
class ProfileAmaPdfEndpointParameters:
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


class ProfileAmaPdfEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = ProfileAmaPdfEndpointParameters

    def run(self):
        LOGGER.debug('Parameters: %s', self._parameters)

        with Database.from_parameters(self._parameters) as database:
            self._run(database)

    def _run(self, database):
        self._set_parameter_defaults()

        query = self._query_for_documents(database)

        query = self._filter(query)

        query_result = query.all()

        response_result = [ row._asdict() for row in query_result]

        self._response_body = self._generate_response_body(response_result)

    def _set_parameter_defaults(self):
        pass


    @classmethod
    def _query_for_documents(cls, database):
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
            ).join(FormField, FormField.form_sub_section == FormSubSection.id
            ).join(Document, Document.id == func.cast(FormField.values[0], Integer))

    def _filter(self, query):
        me_number = self._parameters.query.get('meNumber')[0]
        query = self._filter_by_me_number(query, me_number)

        return query.filter(FormField.type == 'FILE').filter(Document.is_deleted == False)

    @classmethod
    def _filter_by_me_number(cls, query, me_number):
        return query.filter(User.ama_me_number == me_number)
    
    @classmethod
    def _generate_response_body(cls, response_result):
        response_output = {}
        
        if len(response_result) == 0:
            response_output = {"error": "no_record"}
        else:
            response_output = {"result": response_result}
        return response_output
