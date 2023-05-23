import json
from typing import List
from dataclasses import dataclass
from datalabs.parameter import add_schema
from datalabs.task import Task
from datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from datalabs.etl.vericre.profile.column import AMA_PROFILE_COLUMNS

class AMAMetadataTranformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def run(self):
        ama_profiles = self._csv_to_dataframe(self._data[0], encoding="latin")

        ama_metadata = ama_profiles[list(AMA_PROFILE_COLUMNS.keys())].rename(columns=AMA_PROFILE_COLUMNS)

        return [self._dataframe_to_csv(ama_metadata)]

@add_schema
@dataclass
class CAQHStatusURLListTransformerParameters:
    host: str = None
    organization: str = None

class CAQHStatusURLListTransformerTask(Task):
    PARAMETER_CLASS = CAQHStatusURLListTransformerParameters

    def run(self) -> List[str]:
        urls = self._get_caqh_profile_status_url()

        encoded_urls = '\n'.join(urls).encode()

        return [encoded_urls]

    def _get_caqh_profile_status_url(self):
        urls = []

        for dict_bytes_object in self._data:
            dict_data_list = json.loads(dict_bytes_object.decode())

            if isinstance(dict_data_list, dict):
                npi_code = dict_data_list.get('npi', {}).get('npiCode')

                host = self._parameters.host
                organization_id = self._parameters.organization
                url_template = f"https://{host}/RosterAPI/api/providerstatusbynpi?Product=PV&Organization_Id={organization_id}&NPI_Provider_Id={npi_code}"
                urls.append(url_template)

            if isinstance(dict_data_list, list):
                for data in dict_data_list:
                    if isinstance(data, dict):
                        npi_code = data.get('npi', {}).get('npiCode')

                        host = self._parameters.host
                        organization_id = self._parameters.organization
                        url_template = f"https://{host}/RosterAPI/api/providerstatusbynpi?Product=PV&Organization_Id={organization_id}&NPI_Provider_Id={npi_code}"
                        urls.append(url_template)

        return urls



