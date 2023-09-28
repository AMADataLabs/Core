""" Release endpoint classes."""
from   abc import abstractmethod
from   dataclasses import dataclass, asdict
import json
import logging
import sys
import uuid

from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound, APIEndpointException
from   datalabs.access.aws import AWSClient
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

    PROFILE_RESPONSE_MAX_SIZE = 5510


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
                case
                    when ff.is_source_field = True and ff.is_authoritative = True then True
                    else False
                end as is_authoritative,
                ff.is_source_field as is_source,
                ff.name,
                ff.read_only,
                ff.source_key,
                case
                    when ff.is_source_field = True and ff.source = 1 then \'AMA\'
                    when ff.is_source_field = True and ff.source = 2 then \'CAQH\'
                    else \'Physician Provided\'
                end as source_tag,
                ff.type,
                case when ff."type" = 'DATE' then get_formatted_date(ff."values")
                	 else ff."values" 
                end as values,
                ff.option
            from "user" u
            join physician p on u.id = p."user"
            join form_field ff on ff.form = p.form
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

    @run_time_logger
    def _format_query_result(self, query_result):
        response_result = {}

        for record in query_result:
            response_result = self._process_record(response_result, record)

        response_result_keys = list(response_result.keys())
        response_result = [asdict(object) for object in list(response_result.values())]

        response_size = self._get_response_size(response_result)

        next_url = None
        if response_size > StaticTaskParameters.PROFILE_RESPONSE_MAX_SIZE:
            entity_ids = response_result_keys

            request_id, response_result, next_index = self._cache_request(entity_ids, response_result)
            next_url = f'/profile_api/profiles/lookup/{request_id}?index={next_index}'

        response_json = {}
        response_json['profiles'] = response_result

        if next_url is not None:
            response_json['next'] = next_url

        LOGGER.info('Response Result size: %s KB', response_size)

        return response_json

    def _process_record(self, response_result, record):
        if record['ama_entity_id'] not in response_result:
            response_result = self._add_entity_id_in_response(response_result, record)

        record_section = self._format_section_identifier(record['section_identifier'])

        response_result = self._append_record_to_response_result(response_result, record_section, record)

        return response_result

    @run_time_logger
    def _cache_request(self, entity_ids, response_result):
        index = 0
        request_id = ''

        if "POST" == self._parameters.method:
            request_id = str(uuid.uuid4())
            self._save_cache(request_id, entity_ids)
        else:
            request_id = self._parameters.path['request_id']
            index = int(self._parameters.query['index'][0])

        response_parts = []
        for item in response_result:
            response_parts.append(item)
            response_size = self._get_response_size(response_parts)

            if response_size > StaticTaskParameters.PROFILE_RESPONSE_MAX_SIZE:
                response_parts.pop()
                break

        return request_id, response_parts, index + len(response_parts)

    @run_time_logger
    def _save_cache(self, request_id, entity_ids):
        with AWSClient("dynamodb") as dynamodb:
            item = self._generate_item(request_id, entity_ids)
            dynamodb.put_item(TableName=self._parameters.dynamodb_name, Item=item)

    @classmethod
    @run_time_logger
    def _generate_item(cls, request_id, entity_ids):
        item = dict(
            request_id=dict(S=request_id),
            entity_ids=dict(S=(",".join(entity_ids)))
        )

        return item

    @classmethod
    @run_time_logger
    def _get_response_size(cls, response_result):
        size = sys.getsizeof(str(response_result))
        size_in_kb = int(size / 1024)

        return size_in_kb

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
    dynamodb_name: str
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
        entity_id = self._parameters.path.get('entity_id')
        sql = f"{sql} and u.ama_entity_id = '{entity_id}'"

        return sql


# pylint: disable=too-many-instance-attributes
@add_schema(unknowns=True)
@dataclass
class MultiProfileLookupByIndexEndpointParameters:
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
    dynamodb_name: str
    unknowns: dict=None


class MultiProfileLookupByIndexEndpointTask(BaseProfileEndpointTask):
    PARAMETER_CLASS = MultiProfileLookupByIndexEndpointParameters

    def _filter_by_entity_id(self, sql):
        request_id = self._parameters.path['request_id']
        index = int(self._parameters.query['index'][0])

        entity_id = self._get_entity_ids_from_dynamodb(request_id, index)
        LOGGER.info('Entity Ids: %s', entity_id)

        sql = f'''{sql} and u.ama_entity_id in ('{"','".join(entity_id)}')'''

        return sql

    def _get_entity_ids_from_dynamodb(self, request_id, index):
        key=dict(
            request_id=dict(S=request_id)
        )
        response = None

        with AWSClient("dynamodb") as dynamodb:
            response = dynamodb.get_item(
                TableName=self._parameters.dynamodb_name,
                Key=key
            )

        LOGGER.info('Response from DynamoDB: %s', response)

        entity_ids = self._extract_parameters(response)
        entity_id_list = entity_ids.split(',')
        
        return entity_id_list[index:]

    @classmethod
    def _extract_parameters(cls, response):
        parameters = None

        if "Item" in response:
            if "entity_ids" not in response["Item"]:
                raise ValueError(f'Invalid DynamoDB configuration item: {json.dumps(response)}')

            parameters = response["Item"]["entity_ids"]["S"]

        return parameters