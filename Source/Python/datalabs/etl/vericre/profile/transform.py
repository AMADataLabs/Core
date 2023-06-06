""" Tranformer Task for AMAMetadata, CAQHStatusURLList. """
from dataclasses import dataclass
from  datetime import datetime
import json
import logging
import pickle
from   typing import List

from   datalabs.parameter import add_schema
from   datalabs.task import Task

import pdb
logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

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

        statuses = pickle.loads([x[1] for x in pickle.loads(self._data[0])][0])

        active_statuses = [self._select_if_active(status) for status in statuses]

        return [
            self._generate_url(caqh_provider_id, provider_status_date, self._parameters.host, self._parameters.organization).encode() 
            for caqh_provider_id, provider_status_date in active_statuses if caqh_provider_id is not None
        ]


    def _select_if_active(self, status):
        roster_status = status["roster_status"]

        caqh_provider_id = status["caqh_provider_id"]
        provider_status_date = status["provider_status_date"]

        if roster_status == "ACTIVE":
            return caqh_provider_id, provider_status_date
        else:
            LOGGER.info('Ignoring status with roster status:%s', roster_status)
            return None, None


    def _generate_url(self, caqh_provider_id, provider_status_date, host, organization):
        base_url = "https://" + host + "/credentialingapi/api/v8/entities"

        organization_parameter = "organizationId=" + str(organization)
        provider_parameters = "caqhProviderId=" + caqh_provider_id
        attestation_date = datetime.strptime(provider_status_date, '%Y%m%d').strftime("%m/%d/%Y")
        attestation_parameter = "attestationDate=" + attestation_date

        return f"{base_url}?{organization_parameter}&{provider_parameters}&{attestation_parameter}"
