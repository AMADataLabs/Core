""" Release endpoint classes."""
from   dataclasses import dataclass, asdict
from   collections import defaultdict
import json
import logging
import sys
import uuid

from   datalabs.access.api.task import APIEndpointTask, APIEndpointException, ResourceNotFound, InvalidRequest
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
    entity_id: str=None
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
    RECORD_SECTION_NAMES = {
        'medicalSchools': 'medical_schools',
        'medicalTraining': "medical_training",
        'ProviderCDS': "provider_cds",
        'WorkHistory': "work_history",
        "Insurance": "insurance"
    }

    RESPONSE_MAX_SIZE = 5510

    def run(self):
        LOGGER.debug('Parameters: %s', self._parameters)

        with Database.from_parameters(self._parameters) as database:
            self._run(database)

    def _run(self, database):
        query = self._generate_query(self._parameters)

        query_results = self._execute_query(database, query)

        aggregated_records = self._aggregate_records(query_results)

        self._response_body = self._generate_response_body(aggregated_records)

    @classmethod
    def _generate_query(cls, parameters):
        query = cls._generate_base_query()

        query = cls._add_parameter_filters_to_query(query, parameters)

        query = cls._add_sorting_to_query(query)

        return query

    @classmethod
    def _aggregate_records(cls, query_results):
        aggregated_records = defaultdict(ProfileRecords)

        for record in query_results:
            cls._aggregate_record(aggregated_records, record)

        return aggregated_records

    @classmethod
    @run_time_logger
    def _execute_query(cls, database, query):
        query = database.execute(query)
        result = None

        result = [dict(row) for row in query.fetchall()]

        if len(result) == 0:
            raise ResourceNotFound("No profile was found for the provided entity ID")

        return result

    # pylint: disable=no-self-use
    @classmethod
    def _generate_response_body(cls, aggregated_records):
        return {"profiles": [asdict(object) for object in list(aggregated_records.values())]}

    @classmethod
    def _generate_base_query(cls):
        return '''
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

    # pylint: disable=unused-argument
    @classmethod
    def _add_parameter_filters_to_query(cls, query, parameters):
        query = cls._filter_by_active_user(query)

        query = cls._filter_by_hidden_form_field(query)

        return query

    @classmethod
    def _add_sorting_to_query(cls, query):
        query = f'{query} order by u.ama_entity_id asc, ff.sub_section asc, ff.order asc'

        return query

    @classmethod
    def _aggregate_record(cls, aggregated_records, record):
        section_name = cls.RECORD_SECTION_NAMES.get(record['section_identifier'], record['section_identifier'])

        aggregated_records[record['ama_entity_id']].entity_id = record['ama_entity_id']

        cls._append_record_to_aggregated_records(aggregated_records, section_name, record)

        return aggregated_records

    @classmethod
    def _filter_by_active_user(cls, query):
        query = f'{query} and u.is_deleted = False and u.status = \'ACTIVE\''
        return query

    @classmethod
    def _filter_by_hidden_form_field(cls, query):
        query = f'{query} and ff.is_hidden = False'
        return query

    @classmethod
    def _add_entity_id_to_aggregated_records(cls, aggregated_records, entity_id):
        aggregated_records[entity_id].entity_id = entity_id

    @classmethod
    def _append_record_to_aggregated_records(cls, aggregated_records, section_name, record):
        section_items = getattr(aggregated_records[record['ama_entity_id']], section_name)

        if section_items is None:
            section_items = []

        item = cls._create_record_item(record)

        section_items.append(item)

        setattr(aggregated_records[record['ama_entity_id']], section_name, section_items)

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

    @classmethod
    def _add_parameter_filters_to_query(cls, query, parameters):
        query = cls._filter_by_entity_id(query, parameters.path.get("entity_id"))

        return super()._add_parameter_filters_to_query(query, parameters)

    @classmethod
    def _filter_by_entity_id(cls, query, entity_id):
        return f"{query} and u.ama_entity_id = '{entity_id}'"


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
    request_cache_table: str
    payload: dict
    unknowns: dict=None


class MultiProfileLookupEndpointTask(BaseProfileEndpointTask):
    PARAMETER_CLASS = MultiProfileLookupEndpointParameters

    def _generate_response_body(self, aggregated_records):
        response_body = super()._generate_response_body(aggregated_records)
        response_size = self._get_response_size(response_body)
        entity_ids = list(aggregated_records.keys())

        LOGGER.info('Response Result size: %s KB', response_size)

        if response_size > self.RESPONSE_MAX_SIZE:
            request_id = self._save_entity_ids_to_dynamodb(self._parameters.request_cache_table, entity_ids)

            response_body['profiles'] = self._extract_profiles_subset(response_body['profiles'])

            response_body['next'] = self._generate_next_url(request_id, len(response_body['profiles']))

        return response_body

    @classmethod
    def _add_parameter_filters_to_query(cls, query, parameters):
        query = cls._filter_by_entity_ids(query, parameters.payload.get("entity_id"))

        return super()._add_parameter_filters_to_query(query, parameters)

    @classmethod
    def _filter_by_entity_ids(cls, query, entity_ids):
        if not isinstance(entity_ids, list):
            raise InvalidRequest("The entity_id value must be a list of entity IDs.")

        if len(entity_ids) == 0:
            raise InvalidRequest("Please provide at least 1 entity ID.")

        if len(entity_ids) > 1000:
            raise InvalidRequest(
                f"The request contained {len(entity_ids)} entity IDs, but the maximum allowed is 1,000."
            )

        return f'''{query} and u.ama_entity_id in ('{"','".join(entity_ids)}')'''

    @classmethod
    def _get_response_size(cls, aggregated_records):
        size = sys.getsizeof(str(aggregated_records))
        size_in_kb = int(size / 1024)

        return size_in_kb

    @classmethod
    @run_time_logger
    def _save_entity_ids_to_dynamodb(cls, request_cache_table, entity_ids):
        request_id = str(uuid.uuid4())

        with AWSClient("dynamodb") as dynamodb:
            item = cls._generate_item(request_id, entity_ids)
            dynamodb.put_item(TableName=request_cache_table, Item=item)

        return request_id

    @classmethod
    def _extract_profiles_subset(cls, profiles):
        response_parts = []

        for item in profiles:
            response_parts.append(item)

            response_size = cls._get_response_size(response_parts)

            if response_size > cls.RESPONSE_MAX_SIZE:
                response_parts.pop()
                break

        return response_parts

    @classmethod
    def _generate_next_url(cls, request_id, index):
        return f'/profile_api/profiles/lookup/{request_id}?index={index}'

    @classmethod
    @run_time_logger
    def _generate_item(cls, request_id, entity_ids):
        item = dict(
            request_id=dict(S=request_id),
            entity_ids=dict(S=(",".join(entity_ids)))
        )

        return item


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
    request_cache_table: str
    unknowns: dict=None


class MultiProfileLookupByIndexEndpointTask(MultiProfileLookupEndpointTask):
    PARAMETER_CLASS = MultiProfileLookupByIndexEndpointParameters

    def _generate_response_body(self, aggregated_records):
        request_id = self._parameters.path['request_id']
        index = self._parameters.path['request_id']
        response_body = super(MultiProfileLookupEndpointTask, self)._generate_response_body(aggregated_records)
        response_size = self._get_response_size(response_body)

        LOGGER.info('Response Result size: %s KB', response_size)

        if response_size > self.RESPONSE_MAX_SIZE:
            response_body['profiles'] = self._extract_profiles_subset(response_body['profiles'])

            response_body['next'] = self._generate_next_url(request_id, index + len(response_body['profiles']))

        return response_body

    @classmethod
    def _add_parameter_filters_to_query(cls, query, parameters):
        request_cache_table = parameters.request_cache_table
        request_id = parameters.path['request_id']
        index = int(parameters.query['index'][0])
        entity_ids = parameters.query.get("entity_id")

        if request_id:
            entity_ids = cls._get_entity_ids_from_dynamodb(request_cache_table, request_id, index)

        query = cls._filter_by_entity_ids(query, entity_ids)

        return super(MultiProfileLookupEndpointTask, cls)._add_parameter_filters_to_query(query, parameters)

    @classmethod
    def _get_entity_ids_from_dynamodb(cls, request_cache_table, request_id, index):
        response = None
        key = dict(
            request_id=dict(
                S=request_id
            )
        )

        with AWSClient("dynamodb") as dynamodb:
            response = dynamodb.get_item(TableName=request_cache_table, Key=key)

        entity_ids = cls._extract_entity_ids(response)

        return entity_ids.split(',')[index:]

    @classmethod
    def _filter_by_entity_ids(cls, query, entity_ids):
        return f'''{query} and u.ama_entity_id in ('{"','".join(entity_ids)}')'''

    @classmethod
    def _extract_entity_ids(cls, response):
        if "Item" not in response or "entity_ids" not in response["Item"]:
            raise APIEndpointException(f'Invalid DynamoDB configuration item: {json.dumps(response)}')

        return response["Item"]["entity_ids"]["S"]
