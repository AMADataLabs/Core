""" Tranformer Task for AMAMetadata, CAQHStatusURLList. """
from   dataclasses import dataclass
from   datetime import datetime
from   dateutil.parser import isoparse
import json
import logging
import pickle
from   typing import List

import xmltodict

from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.etl.vericre.profile.column import AMA_PROFILE_COLUMNS
from   datalabs.parameter import add_schema
from   datalabs.task import Task

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
        statuses = [json.loads(x[1]) for x in pickle.loads(self._data[0])]

        active_statuses = [status for status in statuses if status["roster_status"] == "ACTIVE"]

        return [self._generate_url(status, self._parameters).encode() for status in active_statuses]

    @classmethod
    def _generate_url(cls, status, parameters):
        base_url = "https://" + parameters.host + "/credentialingapi/api/v8/entities"

        organization_parameter = "organizationId=" + str(parameters.organization)
        provider_parameters = "caqhProviderId=" + status["caqh_provider_id"]
        attestation_date = datetime.strptime(status["provider_status_date"], '%Y%m%d').strftime("%m/%d/%Y")
        attestation_parameter = "attestationDate=" + attestation_date

        return f"{base_url}?{organization_parameter}&{provider_parameters}&{attestation_parameter}"


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class CAQHProfileTransformerParameters:
    execution_time: str


class CAQHProfileTransformerTask(Task):
    PARAMETER_CLASS = CAQHProfileTransformerParameters

    def run(self):
      profiles = [x[1] for x in pickle.loads(self._data[0])]
      current_date = isoparse(self._parameters.execution_time)
      qldb_profiles = self.create_vericre_profile_from_caqh_profile(profiles, current_date)

      return [json.dumps(qldb_profiles).encode()]

    def create_vericre_profile_from_caqh_profile(self, profiles, current_date):
      qldb_profiles = []

      for profile in profiles:
          result_dict = xmltodict.parse(profile)
          qldb_profle = self.create_qldb_profile(result_dict["Provider"], current_date)
          qldb_profiles.append(qldb_profle)

      return qldb_profiles

    def create_qldb_profile(self, profile, current_date):
      transformed_profile = {
        'FutureBoardExamDate': self.create_future_board_exam_date(profile["Specialty"]),
        'TaxID': self.create_tax_id(profile["Practice"]["Tax"]),
        'WorkHistory': self.create_work_history(profile["WorkHistory"]),
        'FirstName': profile.get("FirstName"),
        'OtherName': self.create_other_name(profile["OtherName"]),
        'PreviousInsurance': self.create_previous_insurance(profile["Insurance"], current_date),
        'Languages': self.create_languages(profile["Language"]),
        'ProviderMedicaid': self.create_provider_medicaid(profile["ProviderMedicare"]),
        'TimeGap': self.create_time_gap(profile["TimeGap"]),
        'SSN': profile.get("SSN"),
        'MedicareProviderFlag': profile.get("MedicareProviderFlag"),
        'OtherNameFlag': profile.get("OtherNameFlag"),
        'ProviderMedicare': profile.get("ProviderMedicare"),
        'Insurance': self.create_insurance(profile["Insurance"], current_date),
        'MedicaidProviderFlag': profile.get("MedicaidProviderFlag"),
        'ProviderAddress': self.create_provider_address(profile["ProviderAddress"]),
        'ProviderCDS': self.create_provider_cds(profile["ProviderCDS"]),
        'LastName': profile.get("LastName"),
        'ProviderType': profile.get("ProviderType"),
        'ECFMGIssueDate': profile.get("ECFMGIssueDate")
      }

      return transformed_profile

    def create_future_board_exam_date(self, specialties):
      future_board_exam_date = ''

      for specialty in specialties:
        if specialty["SpecialtyType"]["SpecialtyTypeDescription"] == "Primary":
          if "FutureBoardExamDate" in specialty:
            future_board_exam_date = specialty["FutureBoardExamDate"]

      return future_board_exam_date

    def create_tax_id(self, taxes):
        tax_id = ""

        for tax in taxes:
          if tax.get("TaxType", {}).get("TaxTypeDescription") == "Individual":
            tax_id = tax.get("TaxID", "")
            break

        return tax_id

    def create_work_history(self, work_histories):
      for work_history in work_histories:
        work_history.pop("@ID")

      return sorted(work_histories, key=lambda x: x["StartDate"])

    def create_other_name(self, other_name):
      other_name.pop("@ID")

      return other_name

    def create_previous_insurance(self, insurances, current_date):
      for insurance in insurances:
        insurance.pop("@ID")

      previous_insurances = [insurance for insurance in insurances if datetime.fromisoformat(insurance["EndDate"]) <= current_date]

      return sorted(previous_insurances, key=lambda x: x["StartDate"])

    def create_languages(self, languages):
      return [lang["Language"]["LanguageName"] for lang in languages]

    def create_provider_medicaid(self, provider_medicare):
      provider_medicare.pop("@ID")

      return provider_medicare

    def create_time_gap(self, time_gaps):
      for time_gap in time_gaps:
        time_gap.pop("@ID")

      time_gaps = [time_gap for time_gap in time_gaps if time_gap["GapExplanation"] != "Academic/Training leave"]

      return sorted(time_gaps, key=lambda x: x["StartDate"])

    def create_insurance(self, insurances, current_date):
      insurances = [insurance for insurance in insurances if datetime.fromisoformat(insurance["EndDate"]) > current_date]

      return sorted(insurances, key=lambda x: x["StartDate"])

    def create_provider_address(self, provider_address):
      provider_address.pop("@ID")

      return provider_address

    def create_provider_cds(self, all_provider_cds):
      if isinstance(all_provider_cds, dict):
        all_provider_cds = [all_provider_cds]

      for provider_cds in all_provider_cds:
        provider_cds.pop("@ID")
      modified_all_provider_cds = sorted(all_provider_cds, key=lambda x: x["IssueDate"])

      return modified_all_provider_cds