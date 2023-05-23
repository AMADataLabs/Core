import json
from dataclasses import asdict
from datalabs.etl.vericre.profile.transform import CAQHStatusURLListTransformerTask
from datalabs.etl.vericre.profile.transform import CAQHStatusURLListTransformerParameters


def test_caqh_status_url_list_transformer_task():
    with open('ama_masterfile.json', 'r') as file:
        input_data = json.load(file)

    encoded_data = [json.dumps(data).encode() for data in input_data]

    parameters = CAQHStatusURLListTransformerParameters(host='example.org', organization='123')
    parameters_dict = asdict(parameters)
    task = CAQHStatusURLListTransformerTask(parameters_dict)
    task._data = encoded_data

    result = task.run()

    expected_urls = [
        b'https://example.org/RosterAPI/api/providerstatusbynpi?Product=PV&Organization_Id=123&NPI_Provider_Id=123456009\n'
        b'https://example.org/RosterAPI/api/providerstatusbynpi?Product=PV&Organization_Id=123&NPI_Provider_Id=123456008\n'
        b'https://example.org/RosterAPI/api/providerstatusbynpi?Product=PV&Organization_Id=123&NPI_Provider_Id=123456007'
    ]

    assert result == expected_urls