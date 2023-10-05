""" source: datalabs.access.vericre.api.profiles """
from   collections import namedtuple
import logging

import pytest

from   datalabs.access.api.task import InvalidRequest
from   datalabs.access.vericre.api.profiles import MultiProfileLookupEndpointTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_entity_id_field_must_be_a_list(multi_profile_lookup_event):
    multi_profile_lookup_event["payload"] = dict(entity_id="12345")

    with pytest.raises(Exception) as except_info:
        task = MultiProfileLookupEndpointTask(multi_profile_lookup_event)

        task._add_parameter_filters_to_query(None, task._parameters)

    assert except_info.type == InvalidRequest
    assert str(except_info.value) == 'The entity_id value must be a list of entity IDs.'


# pylint: disable=redefined-outer-name, protected-access
def test_entity_id_count_cannot_be_zero(multi_profile_lookup_event):
    multi_profile_lookup_event["payload"] = dict(entity_id=[])

    with pytest.raises(Exception) as except_info:
        task = MultiProfileLookupEndpointTask(multi_profile_lookup_event)

        task._add_parameter_filters_to_query(None, task._parameters)

    assert except_info.type == InvalidRequest
    assert str(except_info.value) == 'Please provide at least 1 entity ID.'


# pylint: disable=redefined-outer-name, protected-access
def test_entity_id_count_cannot_exceed_1000(multi_profile_lookup_event, over_size_entity_ids):
    multi_profile_lookup_event["payload"] = dict(entity_id=over_size_entity_ids)

    with pytest.raises(Exception) as except_info:
        task = MultiProfileLookupEndpointTask(multi_profile_lookup_event)

        task._add_parameter_filters_to_query(None, task._parameters)

    assert except_info.type == InvalidRequest
    assert str(except_info.value) == 'The request contained 1001 entity IDs, but the maximum allowed is 1,000.'


# # pylint: disable=redefined-outer-name, protected-access
def test_query_results_aggregated_properly(multi_profile_lookup_event, profile_query_results):
    task = MultiProfileLookupEndpointTask(multi_profile_lookup_event)

    aggregated_records = task._aggregate_records(profile_query_results)

    assert len(aggregated_records) == 1


@pytest.fixture
def multi_profile_lookup_event():
    return dict(
        method='',
        path={},
        query={},
        payload={},
        authorization={},
        database_host='',
        database_port='',
        database_backend='',
        database_name='',
        database_username='',
        database_password='',
        request_cache_table=''
    )


@pytest.fixture
def over_size_entity_ids():
    entity_id = []

    for num in range(1001):
        entity_id.append(num)

    return entity_id

@pytest.fixture
def empty_query_result():
    return []

@pytest.fixture
def profile_query_results():
    return [
        {
            "ama_entity_id": '22212056',
            "section_identifier": 'demographics',
            "field_identifier": 'salutation',
            "is_authoritative": False,
            "is_source": False,
            "name": 'Salutation',
            "read_only": False,
            "source_key": None,
            "source_tag": 'Physician Provided',
            "type": 'TEXT',
            "values": [],
            "option": None
        },
        {
            "ama_entity_id": '22212056',
            "section_identifier": 'demographics',
            "field_identifier": 'firstName',
            "is_authoritative": True,
            "is_source": True,
            "name": 'First Name',
            "read_only": False,
            "source_key": 'demographics_firstName',
            "source_tag": 'AMA',
            "type": 'TEXT',
            "values": ['Leilani'],
            "option": None
        }
    ]
