""" Tranformer Task for AMAMetadata, CAQHStatusURLList. """
from   dataclasses import dataclass
from   datetime import datetime
import json
import logging
import pickle
from   typing import List

from   dateutil.parser import isoparse
import pandas
import xmltodict

from   datalabs.etl.csv import CSVReaderMixin
from   datalabs.etl.vericre.profile.column import DEMOG_DATA_COLUMNS, DEA_COLUMNS, ADDRESS_COLUMNS, DEMOGRAPHICS_COLUMNS, MAILING_ADDRESS_COLUMNS
from   datalabs.etl.vericre.profile.column import OFFICE_ADDRESS_COLUMNS, PHONE_COLUMNS, PRACTICE_SPECIALTIES_COLUMNS, NPI_COLUMNS, MEDICAL_SCHOOL_COLUMNS
from   datalabs.etl.vericre.profile.column import ABMS_COLUMNS, MEDICAL_TRAINING_COLUMNS, LICENSES_COLUMNS, LICENSE_NAME_COLUMNS, SANCTIONS_COLUMNS
from   datalabs.etl.vericre.profile.column import MPA_COLUMNS, ECFMG_COLUMNS
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class AMAProfileTransformerParameters:
    execution_time: str = None


class AMAProfileTransformerTask(CSVReaderMixin, Task):
    PARAMETER_CLASS = AMAProfileTransformerParameters

    def run(self):
        abms_data, dea_data, demog_data, license_data, med_sch_data, med_train_data, npi_data, sanctions_data \
            = [self._csv_to_dataframe(d, sep='|') for d in self._data]
        practice_specialties = demog_data[["ENTITY_ID"] + list(PRACTICE_SPECIALTIES_COLUMNS.keys())].copy()
        mpa = demog_data[["ENTITY_ID"] + list(MPA_COLUMNS.keys())].copy()
        ecfmg = demog_data[["ENTITY_ID"] + list(ECFMG_COLUMNS.keys())].copy()


        LOGGER.info("Creating demographics...")
        ama_masterfile = self.create_demographics(demog_data)
        del demog_data

        LOGGER.info("Creating dea...")
        aggregated_dea = self.create_dea(dea_data)
        ama_masterfile = ama_masterfile.merge(aggregated_dea, on="entityId", how="left")
        del dea_data

        LOGGER.info("Creating practiceSpecialties...")
        aggregated_practice_specialities = self.create_practice_specialties(practice_specialties)
        ama_masterfile = ama_masterfile.merge(aggregated_practice_specialities, on="entityId", how="left")
        del practice_specialties

        LOGGER.info("Creating npi...")
        aggregated_npi = self.create_npi(npi_data)
        ama_masterfile = ama_masterfile.merge(aggregated_npi, on="entityId", how="left")
        del npi_data

        LOGGER.info("Creating medicalSchools...")
        aggregated_medical_schools = self.create_medical_schools(med_sch_data)
        ama_masterfile = ama_masterfile.merge(aggregated_medical_schools, on="entityId", how="left")
        del med_sch_data

        LOGGER.info("Creating abms...")
        aggregated_abms = self.create_abms(abms_data)
        ama_masterfile = ama_masterfile.merge(aggregated_abms, on="entityId", how="left")
        del abms_data

        LOGGER.info("Creating medicalTraining...")
        aggregated_medical_training = self.create_medical_training(med_train_data)
        ama_masterfile = ama_masterfile.merge(aggregated_medical_training, on="entityId", how="left")
        del med_train_data

        LOGGER.info("Creating licenses...")
        aggregated_licenses = self.create_licenses(license_data)
        ama_masterfile = ama_masterfile.merge(aggregated_licenses, on="entityId", how="left")
        del license_data

        LOGGER.info("Creating sanctions...")
        aggregated_sanctions = self.create_sanctions(sanctions_data)
        ama_masterfile = ama_masterfile.merge(aggregated_sanctions, on="entityId", how="left")
        del sanctions_data

        LOGGER.info("Creating mpa...")
        aggregated_mpa = self.create_mpa(mpa)
        ama_masterfile = ama_masterfile.merge(aggregated_mpa, on="entityId", how="left")
        del mpa

        LOGGER.info("Creating ecfmg...")
        aggregated_ecfmg = self.create_ecfmg(ecfmg)
        ama_masterfile = ama_masterfile.merge(aggregated_ecfmg, on="entityId", how="left")
        del ecfmg

        LOGGER.info("Generating JSON...")
        return [ama_masterfile.iloc[:1000].to_json(orient="records").encode()]

    @classmethod
    def create_demographics(cls, demog_data):
        demog_data.FIRST_NAME = demog_data.FIRST_NAME.str.strip()
        demog_data.MIDDLE_NAME = demog_data.MIDDLE_NAME.str.strip()
        demog_data.CUT_IND = demog_data.CUT_IND.str.strip()
        demog_data.DEGREE_CD = demog_data.DEGREE_CD.str.strip()
        demog_data.NAT_BRD_YEAR = demog_data.NAT_BRD_YEAR.str.strip()
        demog_data.MAILING_CITY_NM = demog_data.MAILING_CITY_NM.str.strip()
        demog_data.POLO_CITY_NM = demog_data.POLO_CITY_NM.str.strip()
        demog_data.PHONE_PREFIX = demog_data.PHONE_PREFIX.str.strip()
        demog_data.PHONE_EXTENSION = demog_data.PHONE_EXTENSION.str.strip()
        demog_data.PHONE_AREA_CD = demog_data.PHONE_AREA_CD.str.strip()
        demog_data.MPA_DESC = demog_data.MPA_DESC.str.strip()
        demog_data.ECFMG_NBR = demog_data.ECFMG_NBR.str.strip()
        demog_data["EMAIL_ADDRESS"] = demog_data[["EMAIL_NAME", "EMAIL_DOMAIN"]].astype(str).agg('@'.join, axis=1)
        demog_data.EMAIL_ADDRESS[demog_data.EMAIL_NAME.isna()] = None
        demog_data = demog_data[DEMOG_DATA_COLUMNS].copy()

        aggregated_demographics = demog_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        demographics = demog_data[DEMOGRAPHICS_COLUMNS.keys()].rename(columns=DEMOGRAPHICS_COLUMNS)
        mailing_address = demog_data[MAILING_ADDRESS_COLUMNS.keys()].rename(columns=MAILING_ADDRESS_COLUMNS)
        demographics["mailingAddress"] = mailing_address.to_dict(orient="records")
        office_address = demog_data[OFFICE_ADDRESS_COLUMNS.keys()].rename(columns=OFFICE_ADDRESS_COLUMNS)
        office_address["addressUndeliverable"] = None
        demographics["officeAddress"] = office_address.to_dict(orient="records")
        phone = demog_data[PHONE_COLUMNS.keys()].rename(columns=PHONE_COLUMNS)
        demographics["phone"] = phone.to_dict(orient="records")
        aggregated_demographics["demographics"] = demographics.to_dict(orient="records")

        return aggregated_demographics

    @classmethod
    def create_dea(cls, dea_data):
        dea_data["DEA_NBR"] = dea_data.DEA_NBR.str.strip()
        dea_data["DEA_SCHEDULE"] = dea_data.DEA_SCHEDULE.str.strip()
        dea_data["CITY_NM"] = dea_data.CITY_NM.str.strip()
        dea_data["BUSINESS_ACTIVITY"] = dea_data[["BUSINESS_ACTIVITY_CODE", "BUSINESS_ACTIVITY_SUBCODE"]].astype(str).agg('-'.join, axis=1)

        dea = dea_data[DEA_COLUMNS.keys()].rename(columns=DEA_COLUMNS)

        address = dea_data[ADDRESS_COLUMNS.keys()].rename(columns=ADDRESS_COLUMNS)
        address["addressUndeliverable"] = None
        dea["address"] = address.to_dict(orient="records")

        aggregated_dea = dea_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_dea["dea"] = dea.to_dict(orient="records")
        aggregated_dea = aggregated_dea.groupby("entityId")["dea"].apply(list).reset_index()

        aggregated_dea.sort_values('entityId')

        aggregated_dea['dea'] = aggregated_dea['dea'].apply(lambda x: sorted(x, key=lambda item: item['lastReportedDate']))

        return aggregated_dea

    @classmethod
    def create_practice_specialties(cls, demog_data):
        practice_specialties = demog_data[PRACTICE_SPECIALTIES_COLUMNS.keys()].rename(columns=PRACTICE_SPECIALTIES_COLUMNS)
        aggregated_practice_specialties = demog_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_practice_specialties["practiceSpecialties"] = practice_specialties.to_dict(orient="records")

        return aggregated_practice_specialties

    @classmethod
    def create_npi(cls, npi_data):
        # Stop gap for missing END_DT column
        npi_data["END_DT"] = "12/31/2024"

        npi = npi_data[NPI_COLUMNS.keys()].rename(columns=NPI_COLUMNS)

        aggregated_npi = npi_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_npi["npi"] = npi.to_dict(orient="records")
        aggregated_npi = aggregated_npi.groupby("entityId")["npi"].apply(list).reset_index()

        return aggregated_npi

    @classmethod
    def create_medical_schools(cls, med_sch_data):
        med_sch_data.GRAD_STATUS = med_sch_data.GRAD_STATUS.str.strip()
        med_sch_data.GRAD_DT = med_sch_data.GRAD_DT.str.strip()
        med_sch_data.SCHOOL_CD = med_sch_data.SCHOOL_CD.str.strip()
        med_sch_data.GRAD_STATUS[med_sch_data.GRAD_STATUS != "Yes"] = "No"
        medical_schools = med_sch_data[MEDICAL_SCHOOL_COLUMNS.keys()].rename(columns=MEDICAL_SCHOOL_COLUMNS)
        medical_schools["medicalEducationType"] = None
        aggregated_medical_schools = med_sch_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_medical_schools["medicalSchools"] = medical_schools.to_dict(orient="records")
        aggregated_medical_schools = aggregated_medical_schools.groupby("entityId")["medicalSchools"].apply(list).reset_index()

        return aggregated_medical_schools

    @classmethod
    def create_abms(cls, abms_data):
        abms = abms_data[ABMS_COLUMNS.keys()].rename(columns=ABMS_COLUMNS)
        abms["disclaimer"] = "ABMS information is proprietary data maintained in a copyright database compilation owned by the American Board of Medical Specialties.  Copyright (2022) American Board of Medical Specialties.  All rights reserved."
        aggregated_abms = abms_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_abms["abms"] = abms.to_dict(orient="records")
        aggregated_abms = aggregated_abms.groupby("entityId")["abms"].apply(list).reset_index()

        aggregated_abms['abms'] = aggregated_abms['abms'].apply(lambda x: sorted(x, key=lambda item: str(item['effectiveDate']), reverse=True))

        return aggregated_abms

    @classmethod
    def create_medical_training(cls, med_train):
        # Stop gap for missing END_DT column
        med_train["END_DT"] = "12/31/2024"

        medical_training = med_train[MEDICAL_TRAINING_COLUMNS.keys()].rename(columns=MEDICAL_TRAINING_COLUMNS)
        aggregated_medical_training = med_train[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_medical_training["medicalTraining"] = medical_training.to_dict(orient="records")
        aggregated_medical_training = aggregated_medical_training.groupby("entityId")["medicalTraining"].apply(list).reset_index()

        aggregated_medical_training['medicalTraining'] = aggregated_medical_training['medicalTraining'].apply(lambda x: sorted(x, key=lambda item: item['beginDate']))

        return aggregated_medical_training

    @classmethod
    def create_licenses(cls, license_data):
        licenses = license_data[LICENSES_COLUMNS.keys()].rename(columns=LICENSES_COLUMNS)
        license_name = license_data[LICENSE_NAME_COLUMNS.keys()].rename(columns=LICENSE_NAME_COLUMNS)
        licenses["licenseName"] = license_name.to_dict(orient="records")
        aggregated_licenses = license_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_licenses["licenses"] = licenses.to_dict(orient="records")
        aggregated_licenses = aggregated_licenses.groupby("entityId")["licenses"].apply(list).reset_index()

        return aggregated_licenses

    def create_sanctions(self, sanctions):
        sanctions = sanctions[["ENTITY_ID", "BOARD_CD"]]

        non_state_sanctions = sanctions[sanctions.BOARD_CD.isin(["M0", "00", "ZD", "DD", "ZF", "ZA", "ZN", "ZV"])].drop_duplicates().copy()
        aggregated_non_state_sanctions = pandas.DataFrame()
        aggregated_non_state_sanctions["ENTITY_ID"] = non_state_sanctions.ENTITY_ID.unique()

        aggregated_non_state_sanctions = self.aggregate_sanction(aggregated_non_state_sanctions, non_state_sanctions, "M0", "medicareMedicaidSanction")
        aggregated_non_state_sanctions = self.aggregate_sanction(aggregated_non_state_sanctions, non_state_sanctions, "00", "additionalSanction")
        aggregated_non_state_sanctions = self.aggregate_sanction(aggregated_non_state_sanctions, non_state_sanctions, "ZD", "deaSanction")
        aggregated_non_state_sanctions = self.aggregate_sanction(aggregated_non_state_sanctions, non_state_sanctions, "DD", "dodSanction")
        aggregated_non_state_sanctions = self.aggregate_sanction(aggregated_non_state_sanctions, non_state_sanctions, "ZF", "airforceSanction")
        aggregated_non_state_sanctions = self.aggregate_sanction(aggregated_non_state_sanctions, non_state_sanctions, "ZA", "armySanction")
        aggregated_non_state_sanctions = self.aggregate_sanction(aggregated_non_state_sanctions, non_state_sanctions, "ZN", "navySanction")
        aggregated_non_state_sanctions = self.aggregate_sanction(aggregated_non_state_sanctions, non_state_sanctions, "ZV", "vaSanction")
        aggregated_non_state_sanctions["federalSanctions"] = None
        aggregated_non_state_sanctions = aggregated_non_state_sanctions.fillna("N")

        state_sanctions = sanctions[~sanctions.BOARD_CD.isin(["M0", "00", "ZD", "DD", "ZF", "ZA", "ZN", "ZV"])].copy()
        aggregated_state_sanctions = pandas.DataFrame()
        aggregated_state_sanctions["ENTITY_ID"] = state_sanctions.ENTITY_ID.unique()
        aggregated_state_sanctions["state"] = state_sanctions.groupby("ENTITY_ID")["BOARD_CD"].apply(list).reset_index().BOARD_CD
        aggregated_state_sanctions.state[aggregated_state_sanctions.state.isnull()] = aggregated_state_sanctions.state[aggregated_state_sanctions.state.isnull()].apply(lambda x: [])
        aggregated_state_sanctions["stateSanctions"] = aggregated_state_sanctions.state.apply(lambda x: {"state": x})
        aggregated_state_sanctions.drop(columns=["state"], inplace=True)

        aggregated_sanctions = aggregated_state_sanctions.merge(aggregated_non_state_sanctions, on="ENTITY_ID")
        aggregated_sanctions["sanctions"] = aggregated_sanctions[SANCTIONS_COLUMNS].to_dict(orient="records")
        aggregated_sanctions.drop(columns=SANCTIONS_COLUMNS, inplace=True)
        aggregated_sanctions.rename(columns={"ENTITY_ID": "entityId"}, inplace=True)

        return aggregated_sanctions

    @classmethod
    def create_mpa(cls, demog_data):
        mpa = demog_data[MPA_COLUMNS.keys()].rename(columns=MPA_COLUMNS)

        aggregated_mpa = demog_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_mpa["mpa"] = mpa.to_dict(orient="records")

        return aggregated_mpa

    @classmethod
    def create_ecfmg(cls, demog_data):
        ecfmg = demog_data[ECFMG_COLUMNS.keys()].rename(columns=ECFMG_COLUMNS)

        aggregated_ecfmg = demog_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_ecfmg["ecfmg"] = ecfmg.to_dict(orient="records")

        return aggregated_ecfmg

    @classmethod
    def aggregate_sanction(cls, aggregated_sanctions, sanctions, board_code, column):
        sanction = sanctions[sanctions.BOARD_CD == board_code].copy()
        sanction[column] = "Y"

        aggregated_sanctions = aggregated_sanctions.merge(sanction, how="left", on="ENTITY_ID")

        return aggregated_sanctions.drop(columns=["BOARD_CD_x", "BOARD_CD_y"], errors="ignore")

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
        return [self.create_qldb_profile(profile, current_date) for profile in profiles]

    def create_qldb_profile(self, raw_profile, current_date):
        profile = xmltodict.parse(raw_profile)['Provider']

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

    @classmethod
    def create_future_board_exam_date(cls, specialties):
        future_board_exam_date = ''

        for specialty in specialties:
            if specialty["SpecialtyType"]["SpecialtyTypeDescription"] == "Primary":
                if "FutureBoardExamDate" in specialty:
                    future_board_exam_date = specialty["FutureBoardExamDate"]

        return future_board_exam_date

    @classmethod
    def create_tax_id(cls, taxes):
        tax_id = ""

        for tax in taxes:
            if tax.get("TaxType", {}).get("TaxTypeDescription") == "Individual":
                tax_id = tax.get("TaxID", "")
                break

        return tax_id

    @classmethod
    def create_work_history(cls, work_histories):
        for work_history in work_histories:
            work_history.pop("@ID")

        return sorted(work_histories, key=lambda x: x["StartDate"])

    @classmethod
    def create_other_name(cls, other_name):
        other_name.pop("@ID")

        return other_name

    @classmethod
    def create_previous_insurance(cls, insurances, current_date):
        for insurance in insurances:
            insurance.pop("@ID")

        previous_insurances = [
            insurance for insurance in insurances
            if datetime.fromisoformat(insurance["EndDate"]) <= current_date
        ]

        return sorted(previous_insurances, key=lambda x: x["StartDate"])

    @classmethod
    def create_languages(cls, languages):
        return [lang["Language"]["LanguageName"] for lang in languages]

    @classmethod
    def create_provider_medicaid(cls, provider_medicare):
        provider_medicare.pop("@ID")

        return provider_medicare

    @classmethod
    def create_time_gap(cls, time_gaps):
        for time_gap in time_gaps:
            time_gap.pop("@ID")

        time_gaps = [time_gap for time_gap in time_gaps if time_gap["GapExplanation"] != "Academic/Training leave"]

        return sorted(time_gaps, key=lambda x: x["StartDate"])

    @classmethod
    def create_insurance(cls, insurances, current_date):
        insurances = [
            insurance for insurance in insurances
            if datetime.fromisoformat(insurance["EndDate"]) > current_date
        ]

        return sorted(insurances, key=lambda x: x["StartDate"])

    @classmethod
    def create_provider_address(cls, provider_address):
        provider_address.pop("@ID")

        return provider_address

    @classmethod
    def create_provider_cds(cls, all_provider_cds):
        if isinstance(all_provider_cds, dict):
            all_provider_cds = [all_provider_cds]

        for provider_cds in all_provider_cds:
            provider_cds.pop("@ID")
        modified_all_provider_cds = sorted(all_provider_cds, key=lambda x: x["IssueDate"])

        return modified_all_provider_cds
