""" Release endpoint classes."""
from   abc import abstractmethod
from   dataclasses import dataclass, asdict
import json
import logging

from   sqlalchemy import case, literal

from   datalabs.access.api.task import APIEndpointTask
from   datalabs.access.orm import Database
from   datalabs.model.vericre.api import Form, FormField, FormSection, FormSubSection, Physician, User
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


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

class StaticTaskParameters:
    PROFILE_RECORD_SECTION_MAPPING = {
        'medicalSchools': 'medical_schools',
        'medicalTraining': "medical_training",
        'ProviderCDS': "provider_cds",
        'WorkHistory': "work_history",
        "Insurance": "insurance"
    }


class BaseProfileEndpointTask(APIEndpointTask):
    def run(self):
        LOGGER.debug('Parameters: %s', self._parameters)

        with Database.from_parameters(self._parameters) as database:
            self._run(database)

    def _run(self, database, entity_id):
        query = self._query_for_profile(database)

        query = self._filter(query, entity_id)

        query = self._sort(query)

        query_result = [row._asdict() for row in query.all()]

        response_result = self._format_query_result(query_result)

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

    @abstractmethod
    def _filter_by_entity_id(cls, query, entity_id):
        pass

    @classmethod
    def _filter_by_active_user(cls, query):
        return query.filter(User.is_deleted == 'False').filter(User.status == 'ACTIVE')
    
    def _sort(self, query):
        return query.order_by(User.ama_entity_id.asc(), FormField.form_sub_section.asc(), FormField.order.asc())

    def _format_query_result(self, query_result):
        response_result = {}
        for record in query_result:
            if record['ama_entity_id'] not in response_result:
                response_result = self._add_entity_id_in_response(response_result, record)

            record_section = self._format_section_identifier(record['section_identifier'])

            response_result = self._append_record_to_response_result(response_result, record_section, record)

        return [asdict(object) for object in list(response_result.values())]

    @classmethod
    def _add_entity_id_in_response(cls, response_result, record):
        response_result[record['ama_entity_id']] = ProfileRecords(
            entity_id = record['ama_entity_id']
        )

        return response_result
    
    @classmethod
    def _format_section_identifier(cls, section_identifier):
        record_section = None

        if section_identifier in StaticTaskParameters.PROFILE_RECORD_SECTION_MAPPING:
            record_section = StaticTaskParameters.PROFILE_RECORD_SECTION_MAPPING[section_identifier]
        else:
            record_section = section_identifier

        return record_section

    def _append_record_to_response_result(self, response_result, record_section, record):
        if type(None) == type(getattr(response_result[record['ama_entity_id']], record_section)):
            response_result = self._initial_record_section(response_result, record_section, record)

        item = self._create_record_item(record)

        result_list = getattr(response_result[record['ama_entity_id']], record_section)

        result_list.append(item)
        
        setattr(response_result[record['ama_entity_id']], record_section, result_list)
        
        return response_result

    @classmethod
    def _initial_record_section(cls, response_result, record_section, record):
        setattr(response_result[record['ama_entity_id']], record_section, [])

        return response_result

    @classmethod
    def _create_record_item(cls, record):
        return dict(
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

    @classmethod
    def _generate_response_body(cls, response_result):
        return response_result


# pylint: disable=too-many-instance-attributes
@add_schema(unknowns=True)
@dataclass
class LookupMultiProfilesEndpointParameters:
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
    payload: dict
    unknowns: dict=None


class LookupMultiProfilesEndpointTask(BaseProfileEndpointTask):
    PARAMETER_CLASS = LookupMultiProfilesEndpointParameters

    def _run(self, database):
        entity_id = self._parameters.payload.get("entity_id")
        
        super()._run(database, entity_id)

    @classmethod
    def _filter_by_entity_id(cls, query, entity_id):
        return query.filter(User.ama_entity_id.in_(entity_id))


# pylint: disable=too-many-instance-attributes
@add_schema(unknowns=True)
@dataclass
class LookupSingleProfileEndpointParameters:
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


class LookupSingleProfileEndpointTask(BaseProfileEndpointTask):
    PARAMETER_CLASS = LookupSingleProfileEndpointParameters

    def _run(self, database):
        entity_id = self._parameters.path.get('entityId')

        super()._run(database, entity_id)

    @classmethod
    def _filter_by_entity_id(cls, query, entity_id):
        return query.filter(User.ama_entity_id == entity_id)