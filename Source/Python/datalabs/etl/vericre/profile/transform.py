from datalabs.task import Task
import urllib3
import json
import os
from typing import List

class CAQHStatusURLListTranformerTask(Task):

    USERNAME = os.environ.get('USERNAME')
    PASSWORD = os.environ.get('PASSWORD')

    def get_caqh_profile_status_url(self):

        ama_masterfile = json.loads(self._data[0].decode())
        
        host = os.environ.get('HOST')
        organization_id = os.environ.get('ORGANIZATION')
        
        urls = []
        for item in ama_masterfile['item']:
            query_params = item['request']['url']['query']
            
            npi_provider_ids = []
            for param in query_params:
                if param['key'] == 'NPI_Provider_Id':
                    npi_provider_ids.append(param['value'])
            
            for npi_provider_id in npi_provider_ids:
                url_template = "https://{host}/RosterAPI/api/providerstatusbynpi?Product=PV&Organization_Id={organization_id}&NPI_Provider_Id={npi_provider_id}"
                urls.append(url_template.format(
                    host=host,
                    organization_id=organization_id,
                    npi_provider_id=npi_provider_id
                ))
        
        return urls
    
    def run(self) -> List[str]:
      
        urls = self.get_caqh_profile_status_url() 
        
        encoded_urls = '\n'.join(urls).encode()
        
        return [encoded_urls]


