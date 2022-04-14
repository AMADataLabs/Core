""" source: datalabs.access.cpt.api.pla """
import pytest

from   datalabs.access.cpt.api.pla import PLADetailsEndpointTask


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("event")
def test_parameters_are_valid(event):
    PLADetailsEndpointTask(event)
