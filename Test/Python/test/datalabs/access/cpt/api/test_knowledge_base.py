""" source: datalabs.access.cpt.api.consumer_descriptor """
import pytest

from   datalabs.access.api.task import InvalidRequest
from   datalabs.access.cpt.api.knowledge_base import MapSearchEndpointTask


# pylint: disable=redefined-outer-name, protected-access
def test_parameters_are_valid(search_parameters):
    formatted_parameters = MapSearchEndpointTask._get_search_parameters(search_parameters)

    assert formatted_parameters.max_results == 10
    assert formatted_parameters.index == 'SampleIndexName'


# pylint: disable=redefined-outer-name, protected-access
def test_parameters_invalid_parameters_raise_invalid_request(invalid_parameters):
    task = MapSearchEndpointTask(invalid_parameters)

    with pytest.raises(InvalidRequest):
        task.run()


@pytest.fixture
def search_parameters():
    return dict(
        results=10,
        index='SampleIndexName',
        keyword=['test', 'these', 'keywords'],
        section=['test', 'sections'],
        subsection=['test', 'subsections'],
        updated_date_from='2022-01-01',
        updated_date_to='2023-09-10'
    )


@pytest.fixture
def invalid_search_parameters():
    return dict(
        results=None,
        index='SampleIndexName',
        keyword=['test', 'these', 'keywords'],
        section=['test', 'sections'],
        subsection=['test', 'subsections'],
        updated_date_from='2022-01-01',
        updated_date_to='2023-09-10'
    )

@pytest.fixture
def invalid_parameters(invalid_search_parameters):
    return dict(
        method="GET",
        path={},
        query=invalid_search_parameters,
    )

