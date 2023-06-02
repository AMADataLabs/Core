""" Tranformer Task for AMAMetadata, CAQHStatusURLList. """
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
    host: str
    organization: str


class CAQHStatusURLListTransformerTask(Task):
    PARAMETER_CLASS = CAQHStatusURLListTransformerParameters

    def run(self) -> List[str]:
        profiles = json.loads(self._data[0].decode())

        urls = self._generate_caqh_profile_status_urls(profiles, self._parameters.host, self._parameters.organization)

        return ['\n'.join(urls).encode()]

    @classmethod
    def _generate_caqh_profile_status_urls(cls, profiles, host, organization):
        return [cls._generate_url(profile, host, organization) for profile in profiles]

    @classmethod
    def _generate_url(cls, profile, host, organization):
        base_url = "https://" + host + "/RosterAPI/api/providerstatusbynpi"
        product_parameter = "Product=PV"
        organization_parameter = "Organization_Id=" + str(organization)
        npi_parameter = "NPI_Provider_Id=" + str(profile.get('npi').get('npiCode'))

        return f"{base_url}?{product_parameter}&{organization_parameter}&{npi_parameter}"
