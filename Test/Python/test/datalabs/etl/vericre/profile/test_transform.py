""" source: datalabs.etl.vericre.profile.transform """
import json
import pickle

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
def test_caqh_url_list_transformer_task(caqh_profile_statuses):
    host = 'example.org'

    organization_id = '6167'
    url_1 = (
        "https://example.org/credentialingapi/api/v8/entities?"
        "organizationId=6167&caqhProviderId=16038676&attestationDate=08/14/2022"
    )

    expected_urls = [url_1.encode()]

    task = CAQHProfileURLListTranformerTask(
        dict(host=host, organization=organization_id), data=caqh_profile_statuses)

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

# pylint: disable=line-too-long
@pytest.fixture
def caqh_profile_statuses():
    return [
        pickle.dumps(
            [
                (
                    'https://proview-demo.nonprod.caqh.org/RosterAPI/api/providerstatusbynpi?Product=PV&Organization_Id=6166&NPI_Provider_Id=1669768537',
                    b'{"organization_id": "6166", "caqh_provider_id": "16113253", "roster_status": "NOT ON ROSTER", "provider_status": "Expired Attestation", "provider_status_date": "20220814", "provider_practice_state": "IL", "provider_found_flag": "Y"}'
                ),
                (
                    'https://proview-demo.nonprod.caqh.org/RosterAPI/api/providerstatusbynpi?Product=PV&Organization_Id=6166&NPI_Provider_Id=1669768538',
                    b'{"organization_id": "6167", "caqh_provider_id": "16038676", "roster_status": "ACTIVE", "provider_status": "Expired Attestation", "provider_status_date": "20220814", "provider_practice_state": "IL", "provider_found_flag": "Y"}'
                )
            ]
        )
    ]
