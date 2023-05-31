""" Tranformer Task for AMAMetadata, CAQHStatusURLList. """
import json
from dataclasses import dataclass
import pickle
from typing import List
from datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from datalabs.etl.vericre.profile.column import AMA_PROFILE_COLUMNS
from datalabs.parameter import add_schema
from datalabs.task import Task
import pdb

class AMAMetadataTranformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self):
        ama_profiles = self._csv_to_dataframe(self._data[0], encoding="latin")

        ama_metadata = ama_profiles[list(AMA_PROFILE_COLUMNS.keys())].rename(
            columns=AMA_PROFILE_COLUMNS)

        return [self._dataframe_to_csv(ama_metadata)]


@add_schema
@dataclass
class CAQHStatusURLListTransformerParameters:
    host: str = None
    organization: str = None

class CAQHStatusURLListTransformerTask(Task):
    PARAMETER_CLASS = CAQHStatusURLListTransformerParameters

    def run(self) -> List[str]:
        profiles = json.loads(self._data[0].decode())

        host = self._parameters.host
        organization_id = self._parameters.organization
        urls = self._get_caqh_profile_status_urls(
            profiles, host, organization_id)
        encoded_urls = '\n'.join(urls).encode()

        return [encoded_urls]

    @classmethod
    def _get_caqh_profile_status_urls(cls, profiles, host, organization_id):
        base_url = "https://" + host + "/RosterAPI/api/providerstatusbynpi"

        product_param = "Product=PV"
        org_id_param = "Organization_Id=" + str(organization_id)

        def generate_url(profile):
            npi_code = profile.get('npi').get('npiCode')
            npi_param = "NPI_Provider_Id=" + str(npi_code)
            return f"{base_url}?{product_param}&{org_id_param}&{npi_param}"

        urls = list(map(generate_url, profiles))

        return urls
    
class CAQHProfileURLListTranformerTask(Task):
    PARAMETER_CLASS = CAQHStatusURLListTransformerParameters

    def run(self):
        host = self._parameters.host

        organization_id = self._parameters.organization
        pdb.set_trace()
        packed_data = [pickle.loads(pickled_dataset) for pickled_dataset in self._data]
        caqh_provider_ids = self.parse_pickle_data(packed_data)

        urls = self.generate_urls(caqh_provider_ids, host, organization_id)

        return urls
    
    def generate_urls(self, caqh_provider_ids, host, organization_id):
        host = host

        Organization_Id = organization_id  
        urls = []

        for caqh_provider_id in caqh_provider_ids:
            url = f"https://{host}/RosterAPI/api/providerstatus?Product=PV&Organization_Id={Organization_Id}&Caqh_Provider_Id={caqh_provider_id}"
            encoded_url = url.encode()
            urls.append(encoded_url)

        pdb.set_trace()
        return urls

        
    def parse_pickle_data(self, data):
        encoded_data = data[0][0][1]

        decoded_data = encoded_data.decode().strip()
        decoded_data = decoded_data.replace('\xa0', ' ')
        data = json.loads(decoded_data)

        active_provider_ids = [item['caqh_provider_id'] for item in data if item['roster_status'] == 'ACTIVE']

        return active_provider_ids

    
   

