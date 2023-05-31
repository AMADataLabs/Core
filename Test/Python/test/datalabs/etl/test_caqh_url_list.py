""" source: datalabs.etl.vericre.profile.transform """
import json
import pytest
from datalabs.etl.vericre.profile.transform import CAQHProfileURLListTranformerTask
import pdb

def test_caqh_url_list_transformer_task(fixture_input_data):
    host = 'example.org'

    organization_id = '6167'
    caqh_provider_id = '16038676'

    url_1 = f"https://{host}/RosterAPI/api/providerstatus?Product=PV&Organization_Id={organization_id}&Caqh_Provider_Id={caqh_provider_id}"
    url_2 = f"https://{host}/RosterAPI/api/providerstatus?Product=PV&Organization_Id={organization_id}&Caqh_Provider_Id={caqh_provider_id}"
    url_3 = f"https://{host}/RosterAPI/api/providerstatus?Product=PV&Organization_Id={organization_id}&Caqh_Provider_Id={caqh_provider_id}"

    expected_urls = [url_1.encode()]

    task = CAQHProfileURLListTranformerTask(
        dict(host=host, organization=organization_id), data=fixture_input_data)

    result = task.run()

    assert result == expected_urls



@pytest.fixture
def fixture_input_data():
    urls_list = [b'\x80\x04\x95R\x02\x00\x00\x00\x00\x00\x00]\x94\x8c\x1b./caqh_profile_statuses.pkl\x94B(\x02\x00\x00[\r\n  {\r\n    "organization_id": "6166",\r\n    "caqh_provider_id": "16038675",\r\n    "roster_status": "NOT ON ROSTER",\r\n    "provider_status": "Expired Attestation",\r\n    "provider_status_date": "20220814",\r\n    "provider_practice_state": "IL",\r\n    "provider_found_flag": "Y"\r\n  },\r\n  {\r\n    "organization_id": "6167",\r\n    "caqh_provider_id": "16038676",\r\n    "roster_status": "ACTIVE",\r\n    "provider_status": "Expired Attestation",\r\n    "provider_status_date": "20220814",\r\n    "provider_practice_state": "IL",\r\n    "provider_found_flag": "Y"\r\n  }\r\n]\r\n\x94\x86\x94a.']

    return urls_list

