""" source: datalabs.access.vericre.api.profiles """
import logging

import pytest

from   datalabs.access.api.task import APIEndpointException
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
    assert str(except_info.value) == 'Bad Request. The request should have a limit of 1000 Entity Ids'


@pytest.fixture
def over_size_entity_ids():
    entity_id = []

    for num in range(1001):
        entity_id.append(num)

    return entity_id
