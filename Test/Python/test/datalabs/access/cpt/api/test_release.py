""" source: datalabs.access.cpt.api.release """
import pytest

from   datalabs.access.cpt.api.release import ReleasesEndpointTask


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("event")
def test_parameters_are_valid(event):
    ReleasesEndpointTask(event)
