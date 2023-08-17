""" source: datalabs.access.vericre.api.profiles """
from   collections import namedtuple
import logging

import mock
import pytest

from   datalabs.access.api.task import APIEndpointException, ResourceNotFound
from   datalabs.access.vericre.api.profiles import MultiProfileLookupEndpointTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("multi_profile_lookup_event")
def test_verify_entity_id_count(multi_profile_lookup_event, over_size_entity_ids):
    multi_profile_lookup_event["payload"] = dict(entity_id=over_size_entity_ids)

    with pytest.raises(Exception) as except_info:

        task = MultiProfileLookupEndpointTask(multi_profile_lookup_event)

        task._verify_entity_id_count(task._parameters.payload.get('entity_id'))

    assert except_info.type == APIEndpointException
    assert str(except_info.value) == 'Invalid input parameters. The request should have a limit of 1000 Entity Ids'


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("multi_profile_lookup_event")
def test_verify_query_result(multi_profile_lookup_event, empty_query_result):
    multi_profile_lookup_event["payload"] = dict(entityId=['12345678'])

    with pytest.raises(Exception) as except_info:
        task = MultiProfileLookupEndpointTask(multi_profile_lookup_event)

        task._verify_query_result(empty_query_result)

    assert except_info.type == ResourceNotFound
    assert str(except_info.value) == 'The profile was not found for the provided Entity Id'


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("multi_profile_lookup_event")
def test_query_for_profile(multi_profile_lookup_event, profile_query_results):
    multi_profile_lookup_event["path"] = dict(entityId=['12345678'])

    with mock.patch('datalabs.access.vericre.api.profile.Database'):
        session = mock.MagicMock()

        session.execute.return_value = profile_query_results

        task = MultiProfileLookupEndpointTask(multi_profile_lookup_event)

        sql = task._query_for_profile()

        results = session.execute(sql)

    assert (hasattr(results[0], attr) for attr in ['ama_entity_id'])
    assert len(results) == 2


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
    Result = namedtuple('Result', \
        'ama_entity_id section_identifier field_identifier is_authoritative \
        is_source name read_only source_key source_tag type values')

    return [
        Result(
            ama_entity_id = '22212056',
            section_identifier = 'demographics',
            field_identifier = 'salutation',
            is_authoritative = False,
            is_source = False,
            name = 'Salutation',
            read_only = False,
            source_key = None,
            source_tag = 'Physician Provided',
            type = 'TEXT',
            values = []
        ),
        Result(
            ama_entity_id = '22212056',
            section_identifier = 'demographics',
            field_identifier = 'firstName',
            is_authoritative = True,
            is_source = True,
            name = 'First Name',
            read_only = False,
            source_key = 'demographics_firstName',
            source_tag = 'AMA',
            type = 'TEXT',
            values = ['Leilani']
        )
    ]
