""" source: datalabs.etl.vericre.profile.transform """
import json

import pytest

from   datalabs.etl.vericre.profile.transform import CAQHStatusURLListTransformerTask, CAQHProfileURLListTranformerTask
import pdb

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
    pdb.set_trace()
    assert result == expected_urls


# pylint: disable=redefined-outer-name
def test_caqh_url_list_transformer_task(fixture_input_data_status):
    host = 'example.org'

    organization_id = '6167'
    url_1 = (
        f"https://example.org/credentialingapi/api/v8/entities?"
        f"organizationId=6167&caqhProviderId=16038676&attestationDate=08/14/2022"
    )

    expected_urls = [url_1.encode()]

    task = CAQHProfileURLListTranformerTask(
        dict(host=host, organization=organization_id), data=fixture_input_data_status)

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

# pylint: disable=function-redefined, missing-final-newline
@pytest.fixture
def fixture_input_data_status():
    return [b'\x80\x04\x95M\x01\x00\x00\x00\x00\x00\x00]\x94\x8c\x1b./caqh_profile_statuses.pkl\x94B#\x01\x00\x00\x80\x04\x95\x18\x01\x00\x00\x00\x00\x00\x00]\x94(}\x94(\x8c\x0forganization_id\x94\x8c\x046166\x94\x8c\x10caqh_provider_id\x94\x8c\x0816038675\x94\x8c\rroster_status\x94\x8c\rNOT ON ROSTER\x94\x8c\x0fprovider_status\x94\x8c\x13Expired Attestation\x94\x8c\x14provider_status_date\x94\x8c\x0820220814\x94\x8c\x17provider_practice_state\x94\x8c\x02IL\x94\x8c\x13provider_found_flag\x94\x8c\x01Y\x94u}\x94(h\x02\x8c\x046167\x94h\x04\x8c\x0816038676\x94h\x06\x8c\x06ACTIVE\x94h\x08h\th\nh\x0bh\x0ch\rh\x0eh\x0fue.\x94\x86\x94a.']
