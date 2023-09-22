""" Release endpoint classes."""
from   abc import abstractmethod
from   dataclasses import dataclass, asdict
import logging

from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound, APIEndpointException
from   datalabs.access.orm import Database
from   datalabs.parameter import add_schema
from   datalabs.util.profile import run_time_logger
from   datalabs.access.vericre.api.option import OPTION_MAP, OPTION_VALUES_MAP

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
        sql = self._query_for_profile()

        sql = self._filter(sql)

        sql = self._sort(sql)

        query = self._execute_sql(database, sql)

        query_result = self._convert_query_result_to_list(query)

        self._verify_query_result(query_result)

        response_result = self._format_query_result(query_result)

        self._response_body = self._generate_response_body(response_result)

    @classmethod
    def _query_for_profile(cls):
        sql = '''
            select
                u.ama_entity_id,
                ff.sub_section as section_identifier,
                ff.identifier as field_identifier,
                ff.is_authoritative,
                ff.is_source_field as is_source,
                ff.name,
                ff.read_only,
                ff.source_key,
                ff.source as source_tag,
                ff.type,
                ff."values",
                ff.option
            from "user" u
            join physician p on u.id = p."user"
            join form f on p.form = f.id
            join form_field ff on ff.form = f.id 
                and ff.sub_section is not null
            where 1=1
        '''

        return sql

    def _filter(self, sql):
        sql = self._filter_by_entity_id(sql)
        sql = self._filter_by_active_user(sql)
        sql = self._filter_by_hidden_form_field(sql)

        return sql

    @abstractmethod
    def _filter_by_entity_id(self, sql):
        pass

    @classmethod
    def _filter_by_active_user(cls, sql):
        sql = f'{sql} and u.is_deleted = False and u.status = \'ACTIVE\''
        return sql

    @classmethod
    def _filter_by_hidden_form_field(cls, sql):
        sql = f'{sql} and ff.is_hidden = False'
        return sql

    @classmethod
    def _sort(cls, sql):
        sql = f'{sql} order by u.ama_entity_id asc, ff.sub_section asc, ff.order asc'
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
        record_values = record['values']

        if isinstance(record['option'], int) and str(record['option']) in OPTION_MAP:
            record_values = cls._convert_option_values(OPTION_MAP[str(record['option'])], record['values'])

        return dict(
            field_identifier=record['field_identifier'],
            is_authoritative=record['is_authoritative'],
            is_source=record['is_source'],
            name=record['name'],
            read_only=record['read_only'],
            source_key=record['source_key'],
            source_tag=record['source_tag'],
            type=record['type'],
            values=record_values
        )

    @classmethod
    def _convert_option_values(cls, option_key, values):
        option_value_names = []

        for value in values:
            value = value.strip()
            option_values = OPTION_VALUES_MAP[option_key]

            option_value_names = cls._get_option_value_name(option_values, value, option_value_names)

        return option_value_names

    @classmethod
    def _get_option_value_name(cls, option_values, value, option_value_names):
        if value in option_values:
            option_value_names.append(option_values[value])
        else:
            option_value_names.append(value)

        return option_value_names

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

    def _filter_by_entity_id(self, sql):
        entity_id = self._parameters.payload.get("entity_id")

        self._verify_entity_id_count(entity_id)

        sql = f'''{sql} and u.ama_entity_id in ('{"','".join(entity_id)}')'''

        return sql

    @classmethod
    def _verify_entity_id_count(cls, entity_id):
        if not isinstance(entity_id, list):
            raise APIEndpointException("Invalid input parameters. entity_id is not found in the request body")

        if len(entity_id) == 0:
            raise APIEndpointException("Invalid input parameters. Please provide at least 1 Entity Id")

        if len(entity_id) > 1000:
            raise APIEndpointException("Invalid input parameters. The request should have a limit of 1000 Entity Ids")

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

    def _filter_by_entity_id(self, sql):
        entity_id = self._parameters.path.get('entityId')
        sql = f"{sql} and u.ama_entity_id = '{entity_id}'"

        return sql
