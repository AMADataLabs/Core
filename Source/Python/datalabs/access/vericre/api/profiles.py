""" Release endpoint classes."""
from   abc import abstractmethod
from   dataclasses import dataclass, asdict
import logging

from   sqlalchemy import case, literal

from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound, APIEndpointException
from   datalabs.access.orm import Database
from   datalabs.model.vericre.api import Form, FormField, FormSection, FormSubSection, Physician, User
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

# pylint: disable=too-many-instance-attributes
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

    def _run(self, database):
        query = self._query_for_profile(database)

        query = self._filter(query)

        query = self._sort(query)

        query_result = [row._asdict() for row in query.all()]

        self._verify_query_result(query_result)

        response_result = self._format_query_result(query_result)

        self._response_body = self._generate_response_body(response_result)

    @classmethod
    def _query_for_profile(cls, database):
        return database.query(
            User.ama_entity_id,
            FormSubSection.identifier.label('section_identifier'),
            FormField.identifier.label('field_identifier'),
            case(
                [(((FormField.is_source_field == 'True') & (FormField.is_authoritative == 'True')), literal(True))],
                else_=literal(False)
            ).label("is_authoritative"),
            FormField.is_source_field.label('is_source'),
            FormField.name,
            FormField.read_only,
            FormField.source_key,
            case(
                [
                    (((FormField.is_source_field == 'True') & (FormField.source == 1)), 'AMA'),
                    (((FormField.is_source_field == 'True') & (FormField.source == 2)), 'CAQH')
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

    def _filter(self, query):
        query = self._filter_by_entity_id(query)
        query = self._filter_by_active_user(query)

        return query.filter(FormField.is_hidden == 'False')

    @abstractmethod
    def _filter_by_entity_id(self, query):
        pass

    @classmethod
    def _filter_by_active_user(cls, query):
        return query.filter(User.is_deleted == 'False').filter(User.status == 'ACTIVE')

    @classmethod
    def _sort(cls, query):
        return query.order_by(User.ama_entity_id.asc(), FormField.form_sub_section.asc(), FormField.order.asc())

    @classmethod
    def _verify_query_result(cls, query_result):
        if len(query_result) == 0:
            raise ResourceNotFound("The profile was not found for the provided Entity Id")

    def _format_query_result(self, query_result):
        response_result = {}

        for record in query_result:
            response_result = self._process_record(response_result, record)

        return [asdict(object) for object in list(response_result.values())]

    def _process_record(self, response_result, record):
        if record['ama_entity_id'] not in response_result:
            response_result = self._add_entity_id_in_response(response_result, record)

        record_section = self._format_section_identifier(record['section_identifier'])

        response_result = self._append_record_to_response_result(response_result, record_section, record)

        return response_result

    @classmethod
    def _add_entity_id_in_response(cls, response_result, record):
        response_result[record['ama_entity_id']] = ProfileRecords(
            entity_id = record['ama_entity_id']
        )

        return response_result

    @classmethod
    def _format_section_identifier(cls, section_identifier):
        record_section = section_identifier

        if section_identifier in StaticTaskParameters.PROFILE_RECORD_SECTION_MAPPING:
            record_section = StaticTaskParameters.PROFILE_RECORD_SECTION_MAPPING[section_identifier]

        return record_section

    def _append_record_to_response_result(self, response_result, record_section, record):
        result_list = getattr(response_result[record['ama_entity_id']], record_section)

        if result_list is None:
            result_list = []

        item = self._create_record_item(record)

        result_list.append(item)

        setattr(response_result[record['ama_entity_id']], record_section, result_list)

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
class MultiProfileLookupEndpointParameters:
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


class MultiProfileLookupEndpointTask(BaseProfileEndpointTask):
    PARAMETER_CLASS = MultiProfileLookupEndpointParameters

    def _filter_by_entity_id(self, query):
        entity_id = self._parameters.payload.get("entity_id")

        self._verify_entity_id_count(entity_id)

        return query.filter(User.ama_entity_id.in_(entity_id))

    @classmethod
    def _verify_entity_id_count(cls, entity_id):
        if not isinstance(entity_id, list):
            raise APIEndpointException("Bad Request. \"entity_id\" is not found in the request body")
        elif len(entity_id) == 0:
            raise APIEndpointException("Bad Request. Please provide at least 1 Entity Id")
        elif len(entity_id) > 1000:
            raise APIEndpointException("Bad Request. The request should have a limit of 1000 Entity Ids")

# pylint: disable=too-many-instance-attributes
@add_schema(unknowns=True)
@dataclass
class SingleProfileLookupEndpointParameters:
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


class SingleProfileLookupEndpointTask(BaseProfileEndpointTask):
    PARAMETER_CLASS = SingleProfileLookupEndpointParameters

    def _filter_by_entity_id(self, query):
        entity_id = self._parameters.path.get('entityId')

        return query.filter(User.ama_entity_id == entity_id)
