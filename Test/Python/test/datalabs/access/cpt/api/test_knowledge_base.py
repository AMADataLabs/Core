""" source: datalabs.access.cpt.api.consumer_descriptor """
import pytest
from   datalabs.access.cpt.api.knowledge_base import MapSearchEndpointTask


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("search_parameters")
def test_parameters_are_valid(search_parameters):
    formatted_parameters = MapSearchEndpointTask._get_search_parameters(search_parameters)

    assert formatted_parameters.max_results == 50
    assert formatted_parameters.index == 'SampleIndexName'

