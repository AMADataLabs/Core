""" source: datalabs.etl.vericre.profile.transform """
import json
import pytest
from datalabs.etl.vericre.profile.transform import CAQHStatusURLListTransformerTask


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


@pytest.fixture
def fixture_input_data():
    data = [
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

    return [json.dumps(data).encode()]
