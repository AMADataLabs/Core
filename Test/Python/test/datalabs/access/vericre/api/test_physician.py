""" source: datalabs.access.vericre.api.physician """
import logging

import pytest

from   datalabs.access.api.task import InvalidRequest
from   datalabs.access.vericre.api.physician import PhysiciansSearchEndpointTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("physician_event")
def test_generate_search_request_ecfmg_number(physician_event):
    physician_event["payload"] = dict(ecfmg_number='10411247')

    task = PhysiciansSearchEndpointTask(physician_event)

    results = task._generate_search_request(physician_event["payload"])

    assert results == {"applicationId": "vericre", "ecfmgNumber": "10411247"}


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("physician_event")
def test_generate_search_request_npi_number(physician_event):
    physician_event["payload"] = dict(npi_number='1417167750')

    task = PhysiciansSearchEndpointTask(physician_event)

    results = task._generate_search_request(physician_event["payload"])

    assert results == {"applicationId": "vericre", "npiNumber": "1417167750"}


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("physician_event")
def test_generate_search_request_me_number(physician_event):
    physician_event["payload"] = dict(me_number='02501600230')

    task = PhysiciansSearchEndpointTask(physician_event)

    results = task._generate_search_request(physician_event["payload"])

    assert results == {"applicationId": "vericre", "meNumber": "02501600230"}


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("physician_event")
def test_generate_search_request_name(physician_event):
    physician_event["payload"] = dict(first_name='Jon', last_name='Snow', date_of_birth='1947-06-21')

    task = PhysiciansSearchEndpointTask(physician_event)

    results = task._generate_search_request(physician_event["payload"])

    assert results == {
        "applicationId": "vericre",
        "fullName": "Jon Snow",
        "birthDate": "1947-06-21"
    }


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("physician_event")
def test_generate_search_request_name_and_state(physician_event):
    physician_event["payload"] = dict(
        first_name='Ilana',
        last_name='Camhi',
        state_of_practice='FL',
        date_of_birth='19881009'
    )

    task = PhysiciansSearchEndpointTask(physician_event)

    results = task._generate_search_request(physician_event["payload"])

    assert results == {
        "applicationId": "vericre",
        "fullName": "Ilana Camhi",
        "stateCd": "FL",
        "birthDate": "19881009"
    }


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("physician_event")
def test_generate_search_request_invalid(physician_event):
    physician_event["payload"] = dict(first_name='Jon')

    with pytest.raises(Exception) as except_info:
        task = PhysiciansSearchEndpointTask(physician_event)

        task._generate_search_request(physician_event["payload"])

    assert except_info.type == InvalidRequest
    assert str(except_info.value) == (
        "Please provide either a combination of first_name, last_name, "
        "and date_of_birth; or any of npi_number, me_number, or ecfmg_number."
    )
