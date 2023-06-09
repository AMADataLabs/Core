""" Release endpoint classes."""
from   dataclasses import dataclass, asdict
import json
import logging

from   sqlalchemy import case, func, literal
from   sqlalchemy.dialects.postgresql import UUID

from   datalabs.access.api.task import APIEndpointTask
from   datalabs.access.orm import Database
from   datalabs.model.vericre.api import Form, FormField, FormSection, FormSubSection, Physician, User
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=too-many-instance-attributes
@add_schema(unknowns=True)
@dataclass
class ProfilesEndpointParameters:
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
    unknowns: dict=None


@dataclass
class ProfileRecords:
    entity_id: str
    demographics: list=None
    ecfmg: list=None
    medical_schools: list=None
    medical_training: list=None
    licenses: list=None
    sanctions: list=None
    dea: list=None
    abms: list=None
    claim: list=None
    provider_cds: list=None
    work_history: list=None
    insurance: list=None


class BaseProfileEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = ProfilesEndpointParameters

    def run(self):
        LOGGER.debug('Parameters: %s', self._parameters)

        with Database.from_parameters(self._parameters) as database:
            self._run(database)

    def _run(self):
        pass

    @classmethod
    def _generate_response_body(cls, response_result):
        return response_result


class ProfilesEndpointTask(BaseProfileEndpointTask):

    def _run(self):
        method = self._parameters.method

        response_result = f"ProfilesEndpointTask success, method: {method}"
        self._response_body = self._generate_response_body(response_result)


class LookupSingleProfileEndpointTask(BaseProfileEndpointTask):
    def _run(self, database):
        entity_id = self._parameters.path.get('entityId')

        query = self._query_for_profile(database)

        query = self._filter(query, entity_id)

        query = self._sort(query)

        query_result = [row._asdict() for row in query.all()]
        print("query_result===\n", len(query_result))
        print(query_result[0])

        response_result = self._format_query_result(query_result)
        print("=======")
        print(asdict(response_result[entity_id]))
        print("=======")
        
        response_result = [asdict(response_result[entity_id])]
        self._response_body = self._generate_response_body(response_result)

    @classmethod
    def _query_for_profile(cls, database):
        return database.query(
            User.ama_entity_id,
            FormSubSection.identifier.label('section_identifier'),
            FormField.identifier.label('field_identifier'),
            case(
                [(((FormField.is_source_field == True) & (FormField.is_authoritative == True)), literal(True))],
                else_=literal(False)
            ).label("is_authoritative"),
            FormField.is_source_field.label('is_source'),
            FormField.name,
            FormField.read_only,
            FormField.source_key,
            case(
                [
                    (((FormField.is_source_field == True) & (FormField.source == 1)), 'AMA'),
                    (((FormField.is_source_field == True) & (FormField.source == 2)), 'CAQH')
                ],
                else_='Physician Provided'
            ).label("source_tag"),
            FormField.type,
            FormField.values
        ).join(
            FormField, FormField.form_sub_section == FormSubSection.id
        ).join(
            FormSection, FormSection.id == FormSubSection.form_section
        ).join(
            Form, Form.id == FormSection.form
        ).join(
            Physician, Physician.form == Form.id
        ).join(
            User, User.id == Physician.user
        )

    def _filter(self, query, entity_id):
        query = self._filter_by_entity_id(query, entity_id)
        query = self._filter_by_active_user(query)

        return query.filter(FormField.is_hidden == 'False')

    @classmethod
    def _filter_by_entity_id(cls, query, entity_id):
        return query.filter(User.ama_entity_id == entity_id)

    @classmethod
    def _filter_by_active_user(cls, query):
        return query.filter(User.is_deleted == 'False').filter(User.status == 'ACTIVE')
    
    def _sort(self, query):
        return query.order_by(User.ama_entity_id.asc(), FormField.form_sub_section.asc(), FormField.order.asc())

    def _format_query_result(self, query_result):
        response_result_dict = {}
        for record in query_result:
            if record['ama_entity_id'] not in response_result_dict:
                response_result_dict[record['ama_entity_id']] = ProfileRecords(
                    entity_id = record['ama_entity_id']
                )

            item = dict(
                field_identifier = record['field_identifier'],
                is_authoritative = record['is_authoritative'],
                is_source = record['is_source'],
                name = record['name'],
                read_only = record['read_only'],
                source_key = record['source_key'],
                source_tag = record['source_tag'],
                type = record['type'],
                values = record['values']
            )
            
            if 'demographics' == record['section_identifier']:
                if type(None) == type(response_result_dict[record['ama_entity_id']].demographics):
                    response_result_dict[record['ama_entity_id']].demographics = []
                
                response_result_dict[record['ama_entity_id']].demographics.append(item)
        
        return response_result_dict