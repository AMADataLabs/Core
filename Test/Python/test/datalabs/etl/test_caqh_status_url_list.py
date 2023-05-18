import pytest
from datalabs.etl.vericre.profile.transform import CAQHStatusURLListTranformerTask
from datalabs.task import Task

from unittest.mock import patch

class TestCAQHStatusURLListTransformerTask:
    @pytest.fixture
    def task(self):
        task = CAQHStatusURLListTranformerTask(Task)
        task._data = [
            b'{"item": [{"request": {"url": {"query": [{"key": "organizationId", "value": "6166"}, {"key": "caqhProviderId", "value": "16038675"}, {"key": "attestationDate", "value": "08/14/2022"}]},"response": []}},{"name": "Get Status By NPI","request": {"method": "GET","header": [],"url": {"query": [{"key": "Product","value": "PV"},{"key": "Organization_Id","value": "6166"},{"key": "NPI_Provider_Id","value": "1356425755"}]}},"response": []}]}'
        ]
        return task
    
    @patch('os.environ.get')
    def test_get_caqh_profile_status_url(self, mock_environ_get, task):
        mock_environ_get.side_effect = lambda x: {
            'HOST': 'proview-demo.nonprod.caqh.org',
            'ORGANIZATION': '6166'
        }.get(x)
        
        expected_urls = [
            "https://proview-demo.nonprod.caqh.org/RosterAPI/api/providerstatusbynpi?Product=PV&Organization_Id=6166&NPI_Provider_Id=1356425755"
        ]
        
        result = task.get_caqh_profile_status_url()
        
        assert result == expected_urls
