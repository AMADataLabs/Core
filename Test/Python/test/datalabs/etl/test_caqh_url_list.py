""" source: datalabs.etl.vericre.profile.transform """
import json
import pytest
from datalabs.etl.vericre.profile.transform import CAQHProfileURLListTranformerTask

def test_caqh_url_list_transformer_task(fixture_input_data):
    host = 'example.org'
    organization_id = '123'
    caqh_provider_id = '123456009'

    url_1 = f"https://{host}/RosterAPI/api/providerstatus?Product=PV&Organization_Id={organization_id}&Caqh_Provider_Id={caqh_provider_id}"
    url_2 = f"https://{host}/RosterAPI/api/providerstatus?Product=PV&Organization_Id={organization_id}&Caqh_Provider_Id={caqh_provider_id}"
    url_3 = f"https://{host}/RosterAPI/api/providerstatus?Product=PV&Organization_Id={organization_id}&Caqh_Provider_Id={caqh_provider_id}"

    expected_urls = [url_1, url_2, url_3]

    task = CAQHProfileURLListTranformerTask(
        dict(host=host, organization=organization_id), data=fixture_input_data)

    result = task.run()
    assert result == expected_urls



@pytest.fixture
def fixture_input_data():
    urls_list = [
        {
            "organization_id": "6166",
            "caqh_provider_id": "16038675",
            "roster_status": "NOT ON ROSTER",
            "provider_status": "Expired Attestation",
            "provider_status_date": "20220814",
            "provider_practice_state": "IL",
            "provider_found_flag": "Y"
        },
        {
            "organization_id": "6167",
            "caqh_provider_id": "16038676",
            "roster_status": "ACTIVE",
            "provider_status": "Expired Attestation",
            "provider_status_date": "20220814",
            "provider_practice_state": "IL",
            "provider_found_flag": "Y"
        }
    ]

    encoded_data = json.dumps(urls_list).encode()
    return [encoded_data]
