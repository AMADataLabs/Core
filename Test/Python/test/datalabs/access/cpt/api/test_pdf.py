""" source: datalabs.access.cpt.api.pdf """
import pytest

from   datalabs.access.cpt.api.pdf import LatestPDFsEndpointTask


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("event")
def test_parameters_are_valid(event):
    LatestPDFsEndpointTask(event)
