import json
import pytest
from datalabs.etl.vericre.profile.transform import CAQHStatusURLListTransformerTask

def test_caqh_status_url_list_transformer_task(input_data):
    task = CAQHStatusURLListTransformerTask(dict(host='example.org', organization='123'), data=input_data)

    result = task.run()

    expected_urls = [
        b'https://example.org/RosterAPI/api/providerstatusbynpi?Product=PV&Organization_Id=123&NPI_Provider_Id=123456009\n'
        b'https://example.org/RosterAPI/api/providerstatusbynpi?Product=PV&Organization_Id=123&NPI_Provider_Id=123456008\n'
        b'https://example.org/RosterAPI/api/providerstatusbynpi?Product=PV&Organization_Id=123&NPI_Provider_Id=123456007'
    ]

    assert result == expected_urls

@pytest.fixture
def input_data():
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