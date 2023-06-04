""" Tranformer Task for AMAMetadata, CAQHStatusURLList. """
from   dataclasses import dataclass
from   datetime import datetime
import json
import pickle
from   typing import List

from   datalabs.parameter import add_schema
from   datalabs.task import Task
import pdb


@add_schema
@dataclass
class CAQHStatusURLListTransformerParameters:
    host: str
    organization: str


class CAQHStatusURLListTransformerTask(Task):
    PARAMETER_CLASS = CAQHStatusURLListTransformerParameters

    def run(self) -> List[str]:
        profiles = json.loads(self._data[0].decode())

        urls = self._generate_urls(profiles, self._parameters.host, self._parameters.organization)

        return ['\n'.join(urls).encode()]

    @classmethod
    def _generate_urls(cls, profiles, host, organization):
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

        organization = self._parameters.organization

        packed_data = self._data

        pdb.set_trace()

        urls = self._generate_urls(packed_data, host, organization)

        return urls

    # pylint: disable=no-self-use
    def _parse_pickle_data(self, data):
        decoded_data = [pickle.loads(pickled_dataset) for pickled_dataset in data]

        decoded_data = decoded_data[0][0][1].decode()

        parsed_data = json.loads(decoded_data)

        active_provider_ids = [
            item['caqh_provider_id']
            for item in parsed_data
            if item['roster_status'] == 'ACTIVE'
        ]

        return active_provider_ids

    # @classmethod
    # def _generate_urls(cls, statuses, host, organization):
    #     pdb.set_trace()
    #     return [cls._generate_url(status, host, organization) for status in statuses]

    @classmethod
    def _generate_urls(cls, statuses, host, organization):
        parsed_statuses = pickle.loads(statuses[0])
        active_statuses = []

        for status in parsed_statuses:
            roster_status = json.loads(status[1].decode())[0]["roster_status"]
            if roster_status == "ACTIVE":
                active_statuses.append(status)
            else:
                print(f"Ignoring status with roster status: {roster_status}")

        return [cls._generate_url(status, host, organization) for status in active_statuses]

    @classmethod
    def _generate_url(cls, status, host, organization):
        base_url = "https://" + host + "/credentialingapi/api/v8/entities"
        organization_parameter = "organizationId=" + str(organization)
        provider_parameters = "caqhProviderId=" + status["caqh_provider_id"]
        attestation_date = datetime.strptime(status["provider_status_date"], "%Y%m%d").strftime("%m/%d/%Y")
        attestation_parameter = "attestationDate=" + attestation_date

        return f"{base_url}?{organization_parameter}&{provider_parameters}&{attestation_parameter}"


    @classmethod
    def _generate_url(cls, status, host, organization):
        base_url = "https://" + host + "/credentialingapi/api/v8/entities"
        organization_parameter = "organizationId=" + str(organization)
        provider_parameters = "caqhProviderId=" + status["caqh_provider_id"]
        attestation_date = datetime.strptime(status["provider_status_date"], '%Y%m%d').strftime("%m/%d/%Y")
        attestation_parameter = "attestationDate=" + attestation_date

        return f"{base_url}?{organization_parameter}&{provider_parameters}&{attestation_parameter}"
