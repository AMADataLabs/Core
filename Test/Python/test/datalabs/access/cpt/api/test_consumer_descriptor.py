""" source: datalabs.access.cpt.api.consumer_descriptor """
import pytest

from   datalabs.access.cpt.api.consumer_descriptor import ConsumerDescriptorEndpointTask


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("event")
def test_parameters_are_valid(event):
    ConsumerDescriptorEndpointTask(event)
