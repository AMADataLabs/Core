""" Tranformer Task for AMAMetadata, CAQHStatusURLList. """
from   dataclasses import dataclass
from   datetime import datetime
from   dateutil.parser import isoparse
import json
import logging
import pandas
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


import pdb

@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class AMAProfileTransformerParameters:
    execution_time: str = None


class AMAProfileTransformerTask(CSVReaderMixin, Task):
    PARAMETER_CLASS = AMAProfileTransformerParameters

    def run(self):
        print('start')
        documents = [self._csv_to_dataframe(d, sep='|') for d in self._data]
        print('flag 1 done...')

        ama_masterfile = self.create_demographics(documents[2])
        print(len(ama_masterfile))
        print(len(ama_masterfile.drop_duplicates(subset=["entityId"])))

        aggregated_dea = self.create_dea(documents[1])
        print(len(aggregated_dea))
        print(len(aggregated_dea.drop_duplicates(subset=["entityId"])))
        ama_masterfile = ama_masterfile.merge(aggregated_dea, on="entityId", how="left")

        aggregated_practice_specialities = self.create_practice_specialties(documents[2])
        print(len(aggregated_practice_specialities))
        print(len(aggregated_practice_specialities.drop_duplicates(subset=["entityId"])))
        ama_masterfile = ama_masterfile.merge(aggregated_practice_specialities, on="entityId", how="left")

        aggregated_npi = self.create_npi(documents[6])
        print(len(aggregated_npi))
        print(len(aggregated_npi.drop_duplicates(subset=["entityId"])))
        ama_masterfile = ama_masterfile.merge(aggregated_npi, on="entityId", how="left")

        aggregated_medical_schools = self.create_medical_schools(documents[4])
        print(len(aggregated_medical_schools))
        print(len(aggregated_medical_schools.drop_duplicates(subset=["entityId"])))
        ama_masterfile = ama_masterfile.merge(aggregated_medical_schools, on="entityId", how="left")

        aggregated_abms = self.create_abms(documents[0])
        print(len(aggregated_abms))
        print(len(aggregated_abms.drop_duplicates(subset=["entityId"])))
        ama_masterfile = ama_masterfile.merge(aggregated_abms, on="entityId", how="left")

        aggregated_medical_training = self.create_medical_training(documents[5])
        print(len(aggregated_medical_training))
        print(len(aggregated_medical_training.drop_duplicates(subset=["entityId"])))
        ama_masterfile = ama_masterfile.merge(aggregated_medical_training, on="entityId", how="left")

        # Breaks AMA Mastefile
        # aggregated_licenses = self.create_licenses(documents[3])
        # print(len(aggregated_licenses))
        # print(len(aggregated_licenses.drop_duplicates(subset=["entityId"])))
        # ama_masterfile = ama_masterfile.merge(aggregated_licenses, on="entityId", how="left")

        # aggregated_sanctions = self.create_sanctions(documents[7])
        # print('sanctions')
        # print(len(aggregated_sanctions))
        # print(len(aggregated_sanctions.drop_duplicates(subset=["entityId"])))
        # ama_masterfile = ama_masterfile.merge(aggregated_sanctions, on="entityId", how="left")

        aggregated_mpa = self.create_mpa(documents[2])
        print(len(aggregated_mpa))
        print(len(aggregated_mpa.drop_duplicates(subset=["entityId"])))
        ama_masterfile = ama_masterfile.merge(aggregated_mpa, on="entityId", how="left")

        aggregated_ecfmg = self.create_ecfmg(documents[2])
        print(len(aggregated_ecfmg))
        print(len(aggregated_ecfmg.drop_duplicates(subset=["entityId"])))
        ama_masterfile = ama_masterfile.merge(aggregated_ecfmg, on="entityId", how="left")

        return [ama_masterfile.to_json(orient="records").encode()]

    @classmethod
    def create_demographics(cls, demog_data):
        DEMOG_DATA_COLUMNS = [
            "ENTITY_ID",
            "PRIMARY_SPECIALTY",
            "SECONDARY_SPECIALTY",
            "NAME_PREFIX",
            "FIRST_NAME",
            "MIDDLE_NAME",
            "LAST_NAME",
            "NAME_SUFFIX",
            "BIRTH_DT",
            "EMAIL_ADDRESS",
            "DEATH_DT",
            "STUDENT_IND",
            "CUT_IND",
            "STATUS_DESC",
            "PRA_EXPR_DT",
            "DEGREE_CD",
            "NAT_BRD_YEAR",
            "MAILING_ADDRESS_LINE_1",
            "MAILING_ADDRESS_LINE_2",
            "MAILING_ADDRESS_LINE_3",
            "MAILING_CITY_NM",
            "MAILING_STATE_ID",
            "MAILING_ZIP",
            "ADDR_UNDELIVERABLE_IND",
            "POLO_ADDRESS_LINE_1",
            "POLO_ADDRESS_LINE_2",
            "POLO_ADDRESS_LINE_3",
            "POLO_CITY_NM",
            "POLO_STATE_ID",
            "POLO_ZIP",
            "PHONE_PREFIX",
            "PHONE_AREA_CD",
            "PHONE_EXCHANGE",
            "PHONE_NUMBER",
            "PHONE_EXTENSION",
            "MPA_DESC",
            "ECFMG_NBR"
        ]

        DEMOGRAPHICS_COLUMNS = {
            "NAME_PREFIX": "prefix",
            "FIRST_NAME": "firstName",
            "MIDDLE_NAME": "middleName",
            "LAST_NAME": "lastName",
            "NAME_SUFFIX": "suffix",
            "BIRTH_DT": "birthDate",
            "EMAIL_ADDRESS": "emailAddress",
            "DEATH_DT": "deathDate",
            "STUDENT_IND": "studentIndicator",
            "CUT_IND": "cutIndicator",
            "STATUS_DESC": "amaMembershipStatus",
            "PRA_EXPR_DT": "praExpirationDate",
            "DEGREE_CD": "degreeCode",
            "NAT_BRD_YEAR": "nbmeYear"
        }

        MAILING_ADDRESS_COLUMNS = {
            "MAILING_ADDRESS_LINE_1": "line1",
            "MAILING_ADDRESS_LINE_2": "line2",
            "MAILING_ADDRESS_LINE_3": "line3",
            "MAILING_CITY_NM": "city",
            "MAILING_STATE_ID": "state",
            "MAILING_ZIP": "zip",
            "ADDR_UNDELIVERABLE_IND": "addressUndeliverable"
        }

        OFFICE_ADDRESS_COLUMNS = {
            "POLO_ADDRESS_LINE_1": "line1",
            "POLO_ADDRESS_LINE_2": "line2",
            "POLO_ADDRESS_LINE_3": "line3",
            "POLO_CITY_NM": "city",
            "POLO_STATE_ID": "state",
            "POLO_ZIP": "zip",
        }

        PHONE_COLUMNS = {
            "PHONE_PREFIX": "prefix",
            "PHONE_AREA_CD": "areaCode",
            "PHONE_EXCHANGE": "exchange",
            "PHONE_NUMBER": "number",
            "PHONE_EXTENSION": "extension",
        }

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
        DEA_COLUMNS = {
            "DEA_NBR": "deaNumber",
            "DEA_SCHEDULE": "schedule",
            "DEA_AS_OF_DT": "lastReportedDate",
            "DEA_EXPR_DT": "expirationDate",
            "BUSINESS_ACTIVITY": "businessActivity",
            "DEA_STATUS_DESC": "activityStatus",
            "PAYMENT_IND": "paymentInd"
        }

        ADDRESS_COLUMNS = {
            "ADDRESS_LINE_1": "line1",
            "ADDRESS_LINE_2": "line2",
            "ADDRESS_LINE_3": "line3",
            "CITY_NM": "city",
            "STATE_ID": "state",
            "ZIP": "zip"
        }

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

        # Testing
        # e = aggregated_dea.head(5)
        # with open('five_entries_aggregated_dea1.psv', 'w') as file:
        #     file.write(e.to_string())

        # # Convert the 'lastReportedDate' strings to datetime objects for correct sorting
        # e['dea'] = e['dea'].apply(lambda x: x[0])  # Unpack the list (assuming each list contains only one dictionary)
        # e['lastReportedDate'] = pandas.to_datetime(e['dea'].apply(lambda x: x['lastReportedDate']))

        # # Sort the DataFrame by 'lastReportedDate' in ascending order
        # sorted_data = e.sort_values(by='lastReportedDate', ascending=True)
        # with open('five_entries_aggregated_dea-sorted1.psv', 'w') as file:
        #     file.write(sorted_data.to_string())

        # End testing

        print('done!')

        return aggregated_dea

    @classmethod
    def create_practice_specialties(cls, demog_data):
        PRACTICE_SPECIALTIES_COLUMNS = {
            "PRIMARY_SPECIALTY": "primarySpecialty",
            "SECONDARY_SPECIALTY": "secondarySpecialty",
        }

        practice_specialties = demog_data[PRACTICE_SPECIALTIES_COLUMNS.keys()].rename(columns=PRACTICE_SPECIALTIES_COLUMNS)
        aggregated_practice_specialties = demog_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_practice_specialties["practiceSpecialties"] = practice_specialties.to_dict(orient="records")

        return aggregated_practice_specialties

    @classmethod
    def create_npi(cls, npi_data):
        NPI_COLUMNS = {
            "NPI_CD": "npiCode",
            "ENUMERATION_DT": "enumerationDate",
            "DEACTIVATION_DT": "deactivationDate",
            "REACTIVATION_DT": "reactivationDate",
            "REP_NPI_CD": "repNPICode",
            "RPTD_DT": "lastReportedDate",
        }

        npi = npi_data[NPI_COLUMNS.keys()].rename(columns=NPI_COLUMNS)

        aggregated_npi = npi_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_npi["npi"] = npi.to_dict(orient="records")
        aggregated_npi = aggregated_npi.groupby("entityId")["npi"].apply(list).reset_index()

        return aggregated_npi

    @classmethod
    def create_medical_schools(cls, med_sch_data):
        MEDICAL_SCHOOL_COLUMNS = {
            "GRAD_STATUS": "degreeAwarded",
            "SCHOOL_NAME": "schoolName",
            "GRAD_DT": "graduateDate",
            "MATRICULATION_DT": "matriculationDate",
            "DEGREE_CD": "degreeCode",
            "NSC_IND": "nscIndicator"
        }

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
        ABMS_COLUMNS = {
            "CERT_BOARD": "certificateBoard",
            "CERTIFICATE": "certificate",
            "CERTIFICATE_TYPE": "certificateType",
            "EFFECTIVE_DT": "effectiveDate",
            "EXPIRATION_DT": "expirationDate",
            "LAST_REPORTED_DT": "lastReportedDate",
            "REACTIVATION_DT": "reverificationDate",
            "CERT_STAT_DESC": "certificateStatusDescription",
            "DURATION_TYPE_DESC": "durationTypeDescription",
            "MOC_MET_RQT": "meetingMOC",
            "ABMS_RECORD_TYPE": "status"
        }

        abms = abms_data[ABMS_COLUMNS.keys()].rename(columns=ABMS_COLUMNS)
        abms["disclaimer"] = "ABMS information is proprietary data maintained in a copyright database compilation owned by the American Board of Medical Specialties.  Copyright (2022) American Board of Medical Specialties.  All rights reserved."
        aggregated_abms = abms_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_abms["abms"] = abms.to_dict(orient="records")
        aggregated_abms = aggregated_abms.groupby("entityId")["abms"].apply(list).reset_index()

        # TODO: Sorting
        # aggregated_abms['effectiveDate'] = pandas.to_datetime(aggregated_abms['abms'].apply(lambda x: x[0]['effectiveDate']))
        # aggregated_abms_sorted = aggregated_abms.sort_values('effectiveDate', ascending=False)

        return aggregated_abms

    @classmethod
    def create_medical_training(cls, med_train):
        MEDICAL_TRAINING_COLUMNS = {
            "PRIMARY_SPECIALITY": "primarySpecialty",
            "INST_NAME": "institutionName",
            "INST_STATE": "institutionState",
            "BEGIN_DT": "beginDate",
            "END_DT": "endDate",
            "CONFIRM_STATUS": "confirmStatus",
            "INC_MSG": "incMsg",
            "PROGRAM_NM": "programName",
            "TRAINING_TYPE": "trainingType"
        }

        medical_training = med_train[MEDICAL_TRAINING_COLUMNS.keys()].rename(columns=MEDICAL_TRAINING_COLUMNS)
        aggregated_medical_training = med_train[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_medical_training["medicalTraining"] = medical_training.to_dict(orient="records")
        aggregated_medical_training = aggregated_medical_training.groupby("entityId")["medicalTraining"].apply(list).reset_index()

        # TODO: Sorting
        # aggregated_medical_training['beginDate'] = pandas.to_datetime(aggregated_medical_training['medicalTraining'].apply(lambda x: x[0]['beginDate']))
        # aggregated_medical_training_sorted = aggregated_medical_training.sort_values('beginDate')

        return aggregated_medical_training

    @classmethod
    def create_licenses(cls, license_data):
        LICENSES_COLUMNS = {
            "LIC_ISSUE_DT": "issueDate",
            "LIC_EXP_DT": "expirationDate",
            "LIC_AS_OF_DT": "lastReportedDate",
            "LIC_TYPE_DESC": "typeDescription",
            "LIC_STATE_DESC": "stateDescription",
            "DEGREE_CD": "degreeCode",
            "LIC_STATUS_DESC": "licenseStatusDescription",
            "LIC_NBR": "licenseNumber",
            "LIC_RNW_DT": "renewalDate",
        }

        LICENSE_NAME_COLUMNS ={
            "FIRST_NAME": "firstName",
            "MIDDLE_NAME": "middleName",
            "LAST_NAME": "lastName",
            "RPTD_SFX_NM": "suffix",
            "RPTD_FULL_NM": "fullReportedName"
        }

        licenses = license_data[LICENSES_COLUMNS.keys()].rename(columns=LICENSES_COLUMNS)
        license_name = license_data[LICENSE_NAME_COLUMNS.keys()].rename(columns=LICENSE_NAME_COLUMNS)
        licenses["licenseName"] = license_name.to_dict(orient="records")
        aggregated_licenses = license_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_licenses["licenses"] = licenses.to_dict(orient="records")
        aggregated_licenses = aggregated_licenses.groupby("entityId")["licenses"].apply(list).reset_index()

        return aggregated_licenses

    @classmethod
    def create_sanctions(cls, sanctions):
        print("flag 2")

        SANCTIONS_COLUMNS = [
            "medicareMedicaidSanction",
            "federalSanctions",
            "additionalSanction",
            "stateSanctions",
            "deaSanction",
            "dodSanction",
            "airforceSanction",
            "armySanction",
            "navySanction",
            "vaSanction",
        ]

        sanctions = sanctions[["ENTITY_ID", "BOARD_CD"]]
        non_state_sanctions = sanctions[sanctions.BOARD_CD.isin(["M0", "00", "ZD", "DD", "ZF", "ZA", "ZN", "ZV"])].copy()
        non_state_sanctions.loc[:, "medicareMedicaidSanction"] = (non_state_sanctions.BOARD_CD == "M0").map({True: "Y", False: "N"})
        non_state_sanctions.loc[:, "additionalSanction"] = (non_state_sanctions.BOARD_CD == "00").map({True: "Y", False: "N"})
        non_state_sanctions.loc[:, "deaSanction"] = (non_state_sanctions.BOARD_CD == "ZD").map({True: "Y", False: "N"})
        non_state_sanctions.loc[:, "dodSanction"] = (non_state_sanctions.BOARD_CD == "DD").map({True: "Y", False: "N"})
        non_state_sanctions.loc[:, "airforceSanction"] = (non_state_sanctions.BOARD_CD == "ZF").map({True: "Y", False: "N"})
        non_state_sanctions.loc[:, "armySanction"] = (non_state_sanctions.BOARD_CD == "ZA").map({True: "Y", False: "N"})
        non_state_sanctions.loc[:, "navySanction"] = (non_state_sanctions.BOARD_CD == "ZN").map({True: "Y", False: "N"})
        non_state_sanctions.loc[:, "vaSanction"] = (non_state_sanctions.BOARD_CD == "ZV").map({True: "Y", False: "N"})
        non_state_sanctions["federalSanctions"] = None
        non_state_sanctions.drop(columns="BOARD_CD", inplace=True)

        state_sanctions = sanctions[~sanctions.BOARD_CD.isin(["M0", "00", "ZD", "DD", "ZF", "ZA", "ZN", "ZV"])].copy()
        state_sanctions.loc[:, "state"] = state_sanctions.groupby("ENTITY_ID")["BOARD_CD"].apply(list).reset_index().BOARD_CD

        state_sanctions.state[state_sanctions.state.isnull()] = state_sanctions.state[state_sanctions.state.isnull()].apply(lambda x: [])
        state_sanctions.loc[:, "stateSanctions"] = state_sanctions.state.apply(lambda x: {"state": x})
        state_sanctions.drop(columns=["BOARD_CD", "state"], inplace=True)

        flat_sanctions = state_sanctions.merge(non_state_sanctions, on="ENTITY_ID")
        flat_sanctions["sanctions"] = flat_sanctions[SANCTIONS_COLUMNS].to_dict(orient="records")
        flat_sanctions.drop(columns=SANCTIONS_COLUMNS, inplace=True)
        flat_sanctions.rename(columns={"ENTITY_ID": "entityId"}, inplace=True)

        return flat_sanctions

    @classmethod
    def create_mpa(cls, demog_data):
        MPA_COLUMNS = {
            "MPA_DESC": "description"
        }

        mpa = demog_data[MPA_COLUMNS.keys()].rename(columns=MPA_COLUMNS)

        aggregated_mpa = demog_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_mpa["mpa"] = mpa.to_dict(orient="records")

        return aggregated_mpa

    @classmethod
    def create_ecfmg(cls, demog_data):
        ECFMG_COLUMNS = {
            "ECFMG_NBR": "applicantNumber"
        }

        ecfmg = demog_data[ECFMG_COLUMNS.keys()].rename(columns=ECFMG_COLUMNS)

        aggregated_ecfmg = demog_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_ecfmg["ecfmg"] = ecfmg.to_dict(orient="records")

        return aggregated_ecfmg


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

    def create_future_board_exam_date(self, specialties):
      future_board_exam_date = ''

      for specialty in specialties:
        if specialty["SpecialtyType"]["SpecialtyTypeDescription"] == "Primary" and "FutureBoardExamDate" in specialty:
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