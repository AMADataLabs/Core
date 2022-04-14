""" source: datalabs.access.cpt.api.modifier """
import pytest

from   datalabs.access.cpt.api.modifier import ModifierEndpointTask


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("event")
def test_parameters_are_valid(event):
    ModifierEndpointTask(event)
