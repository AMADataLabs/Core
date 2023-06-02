""" source: datalabs.etl.vericre.profile.transform """
import json

import pytest

from   datalabs.etl.vericre.profile.transform import CAQHStatusURLListTransformerTask, CAQHProfileURLListTranformerTask


# pylint: disable=redefined-outer-name, protected-access
def test_caqh_status_url_list_transformer_task(fixture_input_data):
    host = 'example.org'
    organization_id = '123'
    base_url = f'https://{host}/RosterAPI/api/providerstatusbynpi'
    common_params = f'Product=PV&Organization_Id={organization_id}'
    npi_code_1 = '123456009'
    npi_code_2 = '123456008'
    npi_code_3 = '123456007'

    url_1 = f'{base_url}?{common_params}&NPI_Provider_Id={npi_code_1}\n'
    url_2 = f'{base_url}?{common_params}&NPI_Provider_Id={npi_code_2}\n'
    url_3 = f'{base_url}?{common_params}&NPI_Provider_Id={npi_code_3}'

    expected_urls = [url_1.encode() + url_2.encode() + url_3.encode()]

    task = CAQHStatusURLListTransformerTask(
        dict(host=host, organization=organization_id), data=fixture_input_data)

    result = task.run()
    assert result == expected_urls


# pylint: disable=redefined-outer-name
def test_caqh_url_list_transformer_task(fixture_input_data):
    host = 'example.org'

    organization_id = '6167'
    caqh_provider_id = '16038676'

    url_1 = (
        f"https://{host}/RosterAPI/api/providerstatus?"
        f"Product=PV&Organization_Id={organization_id}&Caqh_Provider_Id={caqh_provider_id}"
    )

    expected_urls = [url_1.encode()]

    task = CAQHProfileURLListTranformerTask(
        dict(host=host, organization=organization_id), data=fixture_input_data)

    result = task.run()

    assert result == expected_urls


@pytest.fixture
def fixture_input_data():
    npi_profiles_list = [
        {
            "npi": {
                "npiCode": "123456009"
            }
        },
        {
            "npi": {
                "npiCode": "123456008"
            }
        },
        {
            "npi": {
                "npiCode": "123456007"
            }
        }
    ]

    return [json.dumps(npi_profiles_list).encode()]


@pytest.fixture
def fixture_input_data():
    return [
        b'\x80\x04\x95R\x02\x00\x00\x00\x00\x00\x00]\x94\x8c\x1b./caqh_profile_statuses.pkl\x94B(\x02\x00\x00[\r\n'
        b'  {\r\n    "organization_id": "6166",\r\n    "caqh_provider_id": "16038675",\r\n'
        b'    "roster_status": "NOT ON ROSTER",\r\n    "provider_status": "Expired Attestation",\r\n'
        b'    "provider_status_date": "20220814",\r\n    "provider_practice_state": "IL",\r\n'
        b'    "provider_found_flag": "Y"\r\n  },\r\n'
        b'  {\r\n    "organization_id": "6167",\r\n    "caqh_provider_id": "16038676",\r\n'
        b'    "roster_status": "ACTIVE",\r\n    "provider_status": "Expired Attestation",\r\n'
        b'    "provider_status_date": "20220814",\r\n    "provider_practice_state": "IL",\r\n'
        b'    "provider_found_flag": "Y"\r\n  }\r\n]\r\n\x94\x86\x94a.\n']