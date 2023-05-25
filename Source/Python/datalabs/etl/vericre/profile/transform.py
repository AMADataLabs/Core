""" Transformer base class and CAQHStatusURLList implementation. """
import json
from dataclasses import dataclass
from typing import List

from datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from datalabs.etl.vericre.profile.column import AMA_PROFILE_COLUMNS
from datalabs.parameter import add_schema
from datalabs.task import Task


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
