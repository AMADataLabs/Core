""" source: datalabs.access.cpt.api.clinician_descriptor """
import pytest

from   datalabs.access.cpt.api.clinician_descriptor import \
    ClinicianDescriptorsEndpointTask, \
    AllClinicianDescriptorsEndpointTask


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("event")
def test_clinician_descriptors_parameters_are_valid(event):
    ClinicianDescriptorsEndpointTask(event)


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("event")
def test_all_clinician_descriptors_parameters_are_valid(event):
    AllClinicianDescriptorsEndpointTask(event)
