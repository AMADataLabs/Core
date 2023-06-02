""" Tranformer Task for AMAMetadata, CAQHStatusURLList. """
from   dataclasses import dataclass
from   datetime import datetime
import json
import pickle
from   typing import List

from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.etl.vericre.profile.column import AMA_PROFILE_COLUMNS
from   datalabs.parameter import add_schema
from   datalabs.task import Task


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

        urls = self._get_caqh_profile_status_urls(profiles, self._parameters.host, self._parameters.organization)

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


class CAQHProfileURLListTranformerTask(Task):
    PARAMETER_CLASS = CAQHStatusURLListTransformerParameters

    def run(self):
        host = self._parameters.host

        organization_id = self._parameters.organization

        packed_data = self._data
        caqh_provider_ids = self._parse_pickle_data(packed_data)

        urls = self._generate_urls(caqh_provider_ids, host, organization_id)

        return urls

    # pylint: disable=no-self-use
    def _parse_pickle_data(self, data):
        decoded_data = [pickle.loads(pickled_dataset)
                        for pickled_dataset in data]

        decoded_data = decoded_data[0][0][1].decode()

        parsed_data = json.loads(decoded_data)

        active_provider_ids = [
            item['caqh_provider_id']
            for item in parsed_data
            if item['roster_status'] == 'ACTIVE'
        ]

        return active_provider_ids

    @classmethod
    def _generate_caqh_profile_status_urls(cls, statuses, host, organization):
        return [cls._generate_url(status, host, organization) for status in statuses]

    @classmethod
    def _generate_url(cls, status, host, organization):
        base_url = "https://" + host + "/credentialingapi/api/v8/entities"
        organization_parameter = "organizationId=" + str(organization)
        provider_parameters = "caqhProviderId=" + status["caqh_provider_id"]
        attestation_date = datetime.strptime(status["provider_status_date"], '%Y%m%d').strftime("%m/%d/%Y")
        attestation_parameter = "attestationDate=" + attestation_date

        return f"{base_url}?{organization_parameter}&{provider_parameters}&{attestation_parameter}"
