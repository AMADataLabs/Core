""" source: datalabs.access.cpt.api.consumer_descriptor """
import pytest

from   datalabs.access.api.task import InvalidRequest
from   datalabs.access.cpt.api.knowledge_base import MapSearchEndpointTask, GetArticleEndpointTask


# pylint: disable=redefined-outer-name, protected-access
def test_search_endpoint_authorized_for_explicit_cptkb_year():
    authorizations = dict(CPTKB19=dict(start="2019-01-01T00:00:00-05:00", end="2468-10-11T00:00:00-05:00"))

    assert MapSearchEndpointTask._authorized(authorizations, 2019)


# pylint: disable=redefined-outer-name, protected-access
def test_get_article_endpoint_authorized_for_explicit_cptkb_year():
    authorizations = dict(CPTKB19=dict(start="2019-01-01T00:00:00-05:00", end="2468-10-11T00:00:00-05:00"))

    assert GetArticleEndpointTask._authorized(authorizations, 2019)


# pylint: disable=redefined-outer-name, protected-access
def test_parameters_are_valid(search_parameters):
    formatted_parameters = MapSearchEndpointTask._get_search_parameters(search_parameters)

    assert formatted_parameters.max_results == 10
    assert formatted_parameters.index == 42


# pylint: disable=redefined-outer-name, protected-access
def test_parameters_invalid_results_parameter_raises_invalid_request(search_parameters):
    search_parameters["results"] = 'SomeNonListValue'

    with pytest.raises(InvalidRequest):
        MapSearchEndpointTask._get_search_parameters(search_parameters)


# pylint: disable=redefined-outer-name, protected-access
def test_parameters_invalid_index_parameter_raises_invalid_request(search_parameters):
    search_parameters["index"] = 'SomeNonListValue'

    with pytest.raises(InvalidRequest):
        MapSearchEndpointTask._get_search_parameters(search_parameters)


@pytest.fixture
def search_parameters():
    return dict(
        results=['10'],
        index=['42'],
        keyword=['test', 'these', 'keywords'],
        section=['test', 'sections'],
        subsection=['test', 'subsections'],
        updated_after_date=['2022-01-01'],
        updated_before_date=['2023-09-10']
    )
