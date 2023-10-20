""" Tranformer Task for AMAMetadata, CAQHStatusURLList. """
from   dataclasses import dataclass
from   datetime import datetime
import json
import logging
import pickle
from   typing import List

from   dateutil.parser import isoparse
import numpy
import pandas
import xmltodict

from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.etl.vericre.profile import column
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class DemographicsTransformerParameters:
    execution_time: str = None


class DemographicsTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = DemographicsTransformerParameters

    # pylint: disable=too-many-statements
    def run(self):
        demog_data = self._csv_to_dataframe(self._data[0], sep='|')

        ama_masterfile = self._create_demographics(demog_data)

        ama_masterfile = self._create_practice_specialties(ama_masterfile, demog_data)

        ama_masterfile = self._create_me_number(ama_masterfile, demog_data)

        ama_masterfile = self._create_ecfmg(ama_masterfile, demog_data)

        ama_masterfile = self._create_mpa(ama_masterfile, demog_data)

        return [self._dataframe_to_csv(ama_masterfile)]

    # pylint: disable=too-many-statements
    @classmethod
    def _create_demographics(cls, demog_data):
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
        demog_data["PRINT_NAME"] = demog_data[["FIRST_NAME", "LAST_NAME"]].astype(str).agg(' '.join, axis=1)
        demog_data["EMAIL_ADDRESS"] = demog_data[["EMAIL_NAME", "EMAIL_DOMAIN"]].astype(str).agg('@'.join, axis=1)
        demog_data.EMAIL_ADDRESS[demog_data.EMAIL_NAME.isna()] = None
        demog_data["PRINT_PHONE_NUMBER"] = (
            demog_data[["PHONE_AREA_CD", "PHONE_EXCHANGE", "PHONE_NUMBER"]]
            .astype(str)
            .agg(''.join, axis=1)
        )
        demog_data.PRINT_PHONE_NUMBER[
            demog_data.PHONE_AREA_CD.isna() | demog_data.PHONE_EXCHANGE.isna() | demog_data.PHONE_NUMBER.isna()
        ] = None

        demog_data = demog_data[column.DEMOG_DATA_COLUMNS].copy()

        mailing_address = \
            demog_data[column.MAILING_ADDRESS_COLUMNS.keys()].rename(columns=column.MAILING_ADDRESS_COLUMNS)
        demog_data["MAILING_ADDRESS"] = mailing_address.to_json(orient="records")

        office_address = demog_data[column.OFFICE_ADDRESS_COLUMNS.keys()].rename(columns=column.OFFICE_ADDRESS_COLUMNS)
        office_address["addressUndeliverable"] = None
        demog_data["OFFICE_ADDRESS"] = office_address.to_json(orient="records")

        phone = demog_data[column.PHONE_COLUMNS.keys()].rename(columns=column.PHONE_COLUMNS)
        demog_data["PHONE"] = phone.to_json(orient="records")

        demographics = demog_data[column.DEMOGRAPHICS_COLUMNS.keys()].rename(columns=column.DEMOGRAPHICS_COLUMNS)

        aggregated_demographics = demog_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_demographics["demographics"] = demographics.to_json(orient="records")

        return aggregated_demographics

    @classmethod
    def _create_me_number(cls, ama_masterfile, demog_data):
        me_number = demog_data[column.ME_NUMBER_COLUMNS.keys()].rename(columns=column.ME_NUMBER_COLUMNS).copy()

        ama_masterfile = ama_masterfile.merge(me_number, on="entityId", how="left")

        return ama_masterfile

    @classmethod
    def _create_practice_specialties(cls, ama_masterfile, demog_data):
        practice_specialties = demog_data[["ENTITY_ID"] + list(column.PRACTICE_SPECIALTIES_COLUMNS.keys())].copy()
        practice_specialties \
            = demog_data[column.PRACTICE_SPECIALTIES_COLUMNS.keys()].rename(columns=column.PRACTICE_SPECIALTIES_COLUMNS)
        aggregated_practice_specialties = demog_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_practice_specialties["practiceSpecialties"] = practice_specialties.to_json(orient="records")

        ama_masterfile = ama_masterfile.merge(aggregated_practice_specialties, on="entityId", how="left")

        return ama_masterfile

    @classmethod
    def _create_ecfmg(cls, ama_masterfile, demog_data):
        ecfmg = demog_data[["ENTITY_ID"] + list(column.ECFMG_COLUMNS.keys())].copy()
        ecfmg = demog_data[column.ECFMG_COLUMNS.keys()].rename(columns=column.ECFMG_COLUMNS)
        aggregated_ecfmg = demog_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_ecfmg["ecfmg"] = ecfmg.to_json(orient="records")

        ama_masterfile = ama_masterfile.merge(aggregated_ecfmg, on="entityId", how="left")

        return ama_masterfile

    @classmethod
    def _create_mpa(cls, ama_masterfile, demog_data):
        mpa = demog_data[["ENTITY_ID"] + list(column.MPA_COLUMNS.keys())].copy()
        mpa = demog_data[column.MPA_COLUMNS.keys()].rename(columns=column.MPA_COLUMNS)
        aggregated_mpa = demog_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_mpa["mpa"] = mpa.to_json(orient="records")

        ama_masterfile = ama_masterfile.merge(aggregated_mpa, on="entityId", how="left")

        return ama_masterfile

    @classmethod
    def _pickle_masterfile(cls, ama_masterfile):
        for column_name in ["demographics", "mpa", "ecfmg", "meNumber", "practiceSpecialties"]:
            ama_masterfile.loc[:, column_name] = ama_masterfile.loc[:, column_name].apply(pickle.dumps)

        return ama_masterfile


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class DeaTransformerParameters:
    execution_time: str = None


class DeaTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = DeaTransformerParameters

    def run(self):
        dea_data = self._csv_to_dataframe(self._data[0], sep='|')

        ama_masterfile = self._create_dea(dea_data)

        ama_masterfile = self._fill_nulls(ama_masterfile)

        # ama_masterfile = self._pickle_masterfile(ama_masterfile)

        return [self._dataframe_to_csv(ama_masterfile)]

    @classmethod
    def _create_dea(cls, dea_data):
        dea_data["DEA_NBR"] = dea_data.DEA_NBR.str.strip()
        dea_data["DEA_SCHEDULE"] = dea_data.DEA_SCHEDULE.str.strip()
        dea_data["CITY_NM"] = dea_data.CITY_NM.str.strip()
        dea_data["BUSINESS_ACTIVITY"] \
            = dea_data[["BUSINESS_ACTIVITY_CODE", "BUSINESS_ACTIVITY_SUBCODE"]].astype(str).agg('-'.join, axis=1)

        dea = dea_data[column.DEA_COLUMNS.keys()].rename(columns=column.DEA_COLUMNS)

        address = dea_data[column.ADDRESS_COLUMNS.keys()].rename(columns=column.ADDRESS_COLUMNS)
        address["addressUndeliverable"] = None
        dea["address"] = address.to_json(orient="records")

        aggregated_dea = dea_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_dea["dea"] = dea.to_json(orient="records")
        aggregated_dea = aggregated_dea.groupby("entityId")["dea"].apply(list).reset_index()

        aggregated_dea.sort_values('entityId')

        aggregated_dea['dea'] = aggregated_dea['dea'].apply(
            lambda x: sorted(x, key=lambda item: str(item['lastReportedDate']))
        )

        return aggregated_dea

    @classmethod
    def _fill_nulls(cls, ama_masterfile):
        ama_masterfile.dea = ama_masterfile.dea.fillna("").apply(list)

        return ama_masterfile

    @classmethod
    def _pickle_masterfile(cls, ama_masterfile):
        ama_masterfile.loc[:, "dea"] = ama_masterfile.loc[:, "dea"].apply(pickle.dumps)

        return ama_masterfile


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class NPITransformerParameters:
    execution_time: str = None


class NPITransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = NPITransformerParameters

    def run(self):
        npi_data = self._csv_to_dataframe(self._data[0], sep='|')

        ama_masterfile = self._create_npi(npi_data)

        ama_masterfile = self._fill_nulls(ama_masterfile)

        # ama_masterfile = self._pickle_masterfile(ama_masterfile)

        return [self._dataframe_to_csv(ama_masterfile.reset_index())]

    @classmethod
    def _create_npi(cls, npi_data):
        npi_data.sort_values(by=['RPTD_DT'], ascending=False, inplace=True)
        npi_data.drop_duplicates(subset="ENTITY_ID", inplace=True)
        npi = npi_data[column.NPI_COLUMNS.keys()].rename(columns=column.NPI_COLUMNS)

        aggregated_npi = npi_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_npi["npi"] = npi.to_json(orient="records")

        return aggregated_npi

    @classmethod
    def _fill_nulls(cls, ama_masterfile):
        ama_masterfile.loc[ama_masterfile.npi.isnull(), "npi"] = \
            ama_masterfile.loc[ama_masterfile.npi.isnull(), "npi"].apply(
                lambda x: {}
            )

        return ama_masterfile

    @classmethod
    def _pickle_masterfile(cls, ama_masterfile):
        ama_masterfile.loc[:, "npi"] = ama_masterfile.loc[:, "npi"].apply(pickle.dumps)

        return ama_masterfile


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class MedicalSchoolsTransformerParameters:
    execution_time: str = None


class MedicalSchoolsTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = MedicalSchoolsTransformerParameters

    def run(self):
        med_sch_data = self._csv_to_dataframe(self._data[0], sep='|')

        ama_masterfile = self._create_medical_schools(med_sch_data)

        ama_masterfile = self._fill_nulls(ama_masterfile)

        # ama_masterfile = self._pickle_masterfile(ama_masterfile)

        return [self._dataframe_to_csv(ama_masterfile)]

    @classmethod
    def _create_medical_schools(cls, med_sch_data):
        med_sch_data.GRAD_STATUS = med_sch_data.GRAD_STATUS.str.strip()
        med_sch_data.GRAD_DT = med_sch_data.GRAD_DT.str.strip()
        med_sch_data.SCHOOL_CD = med_sch_data.SCHOOL_CD.str.strip()
        med_sch_data.GRAD_STATUS[med_sch_data.GRAD_STATUS != "Yes"] = "No"
        medical_schools = \
            med_sch_data[column.MEDICAL_SCHOOL_COLUMNS.keys()].rename(columns=column.MEDICAL_SCHOOL_COLUMNS)
        medical_schools["medicalEducationType"] = None
        aggregated_medical_schools = med_sch_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_medical_schools["medicalSchools"] = medical_schools.to_json(orient="records")
        aggregated_medical_schools \
            = aggregated_medical_schools.groupby("entityId")["medicalSchools"].apply(list).reset_index()

        aggregated_medical_schools['medicalSchools'] = aggregated_medical_schools['medicalSchools'].apply(
            lambda x: sorted(x, key=lambda item: str(item['graduateDate']))
        )

        return aggregated_medical_schools

    @classmethod
    def _fill_nulls(cls, ama_masterfile):
        ama_masterfile.medicalSchools = ama_masterfile.medicalSchools.fillna("").apply(list)

        return ama_masterfile

    @classmethod
    def _pickle_masterfile(cls, ama_masterfile):
        ama_masterfile.loc[:, "medicalSchools"] = ama_masterfile.loc[:, "medicalSchools"].apply(pickle.dumps)

        return ama_masterfile


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ABMSTransformerParameters:
    execution_time: str = None


class ABMSTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = ABMSTransformerParameters

    def run(self):
        abms_data = self._csv_to_dataframe(self._data[0], sep='|')

        ama_masterfile = self._create_abms(abms_data)

        ama_masterfile = self._fill_nulls(ama_masterfile)

        # ama_masterfile = self._pickle_masterfile(ama_masterfile)

        return [self._dataframe_to_csv(ama_masterfile)]

    @classmethod
    def _create_abms(cls, abms_data):
        abms = abms_data[column.ABMS_COLUMNS.keys()].rename(columns=column.ABMS_COLUMNS)
        abms["disclaimer"] = "ABMS information is proprietary data maintained in a copyright database "
        abms["disclaimer"] += "compilation owned by the American Board of Medical Specialties.  "
        abms["disclaimer"] += "Copyright (2022) American Board of Medical Specialties.  All rights reserved."
        aggregated_abms = abms_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_abms["abms"] = abms.to_json(orient="records")
        aggregated_abms = aggregated_abms.groupby("entityId")["abms"].apply(list).reset_index()

        aggregated_abms['abms'] = aggregated_abms['abms'].apply(
            lambda x: sorted(x, key=lambda item: str(item['effectiveDate']), reverse=True)
        )

        return aggregated_abms

    @classmethod
    def _fill_nulls(cls, ama_masterfile):
        ama_masterfile.abms = ama_masterfile.abms.fillna("").apply(list)

        return ama_masterfile

    @classmethod
    def _pickle_masterfile(cls, ama_masterfile):
        ama_masterfile.loc[:, "abms"] = ama_masterfile.loc[:, "abms"].apply(pickle.dumps)

        return ama_masterfile


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class MedicalTrainingTransformerParameters:
    execution_time: str = None


class MedicalTrainingTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = MedicalTrainingTransformerParameters

    def run(self):
        med_train_data = self._csv_to_dataframe(self._data[0], sep='|')

        ama_masterfile = self._create_medical_training(med_train_data)

        ama_masterfile = self._fill_nulls(ama_masterfile)

        # ama_masterfile = self._pickle_masterfile(ama_masterfile)

        return [self._dataframe_to_csv(ama_masterfile)]

    @classmethod
    def _create_medical_training(cls, med_train):
        medical_training = \
            med_train[column.MEDICAL_TRAINING_COLUMNS.keys()].rename(columns=column.MEDICAL_TRAINING_COLUMNS)
        aggregated_medical_training = med_train[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_medical_training["medicalTraining"] = medical_training.to_json(orient="records")
        aggregated_medical_training \
            = aggregated_medical_training.groupby("entityId")["medicalTraining"].apply(list).reset_index()

        aggregated_medical_training['medicalTraining'] = aggregated_medical_training['medicalTraining'].apply(
            lambda x: sorted(x, key=lambda item: item['beginDate'])
        )

        return aggregated_medical_training

    @classmethod
    def _fill_nulls(cls, ama_masterfile):
        ama_masterfile.medicalTraining = ama_masterfile.medicalTraining.fillna("").apply(list)

        return ama_masterfile

    @classmethod
    def _pickle_masterfile(cls, ama_masterfile):
        ama_masterfile.loc[:, "medicalTraining"] = ama_masterfile.loc[:, "medicalTraining"].apply(pickle.dumps)

        return ama_masterfile


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class LicensesTransformerParameters:
    execution_time: str = None


class LicensesTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = LicensesTransformerParameters

    def run(self):
        license_data = self._csv_to_dataframe(self._data[0], sep='|')

        ama_masterfile = self._create_licenses(license_data)

        ama_masterfile = self._fill_nulls(ama_masterfile)

        # ama_masterfile = self._pickle_masterfile(ama_masterfile)

        return [self._dataframe_to_csv(ama_masterfile)]

    @classmethod
    def _create_licenses(cls, license_data):
        licenses = license_data[column.LICENSES_COLUMNS.keys()].rename(columns=column.LICENSES_COLUMNS)
        license_name = license_data[column.LICENSE_NAME_COLUMNS.keys()].rename(columns=column.LICENSE_NAME_COLUMNS)
        licenses["licenseName"] = license_name.to_json(orient="records")
        aggregated_licenses = license_data[["ENTITY_ID"]].rename(columns={"ENTITY_ID": "entityId"})
        aggregated_licenses["licenses"] = licenses.to_json(orient="records")
        aggregated_licenses = aggregated_licenses.groupby("entityId")["licenses"].apply(list).reset_index()

        aggregated_licenses['licenses'] \
            = aggregated_licenses['licenses'].apply(lambda x: sorted(x, key=lambda item: str(item['issueDate'])))

        return aggregated_licenses

    @classmethod
    def _fill_nulls(cls, ama_masterfile):
        ama_masterfile.licenses = ama_masterfile.licenses.fillna("").apply(list)

        return ama_masterfile

    @classmethod
    def _pickle_masterfile(cls, ama_masterfile):
        ama_masterfile.loc[:, "licenses"] = ama_masterfile.loc[:, "licenses"].apply(pickle.dumps)

        return ama_masterfile


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class SanctionsTransformerParameters:
    execution_time: str = None


class SanctionsTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = SanctionsTransformerParameters

    def run(self):
        sanctions_data = self._csv_to_dataframe(self._data[0], sep='|')

        ama_masterfile = self._create_sanctions(sanctions_data)

        ama_masterfile = self._fill_null_sanctions(ama_masterfile)

        # ama_masterfile = self._pickle_masterfile(ama_masterfile)

        return [self._dataframe_to_csv(ama_masterfile)]

    @classmethod
    def _create_sanctions(cls, sanctions):
        sanctions = sanctions[["ENTITY_ID", "BOARD_CD"]]

        aggregated_non_state_sanctions = cls._create_non_state_sanctions(sanctions)

        aggregated_state_sanctions = cls._create_state_sanctions(sanctions)

        aggregated_sanctions = cls._merge_sanctions(aggregated_non_state_sanctions, aggregated_state_sanctions)

        return aggregated_sanctions

    @classmethod
    def _create_non_state_sanctions(cls, sanctions):
        non_state_sanctions = (sanctions[sanctions.BOARD_CD.isin(["M0", "00", "ZD", "DD", "ZF", "ZA", "ZN", "ZV"])]
            .drop_duplicates().copy())
        aggregated_non_state_sanctions = pandas.DataFrame()
        aggregated_non_state_sanctions["ENTITY_ID"] = non_state_sanctions.ENTITY_ID.unique()

        aggregated_non_state_sanctions = cls._aggregate_sanction(
            aggregated_non_state_sanctions, non_state_sanctions, "M0", "medicareMedicaidSanction")

        aggregated_non_state_sanctions = cls._aggregate_sanction(
            aggregated_non_state_sanctions, non_state_sanctions, "00", "additionalSanction")

        aggregated_non_state_sanctions = cls._aggregate_sanction(
            aggregated_non_state_sanctions, non_state_sanctions, "ZD", "deaSanction")

        aggregated_non_state_sanctions = cls._aggregate_sanction(
            aggregated_non_state_sanctions, non_state_sanctions, "DD", "dodSanction")

        aggregated_non_state_sanctions = cls._aggregate_sanction(
            aggregated_non_state_sanctions, non_state_sanctions, "ZF", "airforceSanction")

        aggregated_non_state_sanctions = cls._aggregate_sanction(
            aggregated_non_state_sanctions, non_state_sanctions, "ZA", "armySanction")

        aggregated_non_state_sanctions = cls._aggregate_sanction(
            aggregated_non_state_sanctions, non_state_sanctions, "ZN", "navySanction")

        aggregated_non_state_sanctions = cls._aggregate_sanction(
            aggregated_non_state_sanctions, non_state_sanctions, "ZV", "vaSanction")

        aggregated_non_state_sanctions["federalSanctions"] = None

        return aggregated_non_state_sanctions

    @classmethod
    def _create_state_sanctions(cls, sanctions):
        state_sanctions = sanctions[~sanctions.BOARD_CD.isin(["M0", "00", "ZD", "DD", "ZF", "ZA", "ZN", "ZV"])].copy()
        aggregated_state_sanctions = pandas.DataFrame()

        aggregated_state_sanctions["ENTITY_ID"] = state_sanctions.ENTITY_ID.unique()

        aggregated_state_sanctions["state"] \
            = state_sanctions.groupby("ENTITY_ID")["BOARD_CD"].apply(list).reset_index().BOARD_CD

        aggregated_state_sanctions.state[aggregated_state_sanctions.state.isnull()] \
            = aggregated_state_sanctions.state[aggregated_state_sanctions.state.isnull()].apply(lambda x: [])

        aggregated_state_sanctions["stateSanctionsValue"] = "ACTION REPORTED"
        aggregated_state_sanctions["stateSanctionsValue"][aggregated_state_sanctions.state.isnull()] = \
            "NO ACTIONS REPORTED AT THIS TIME"

        aggregated_state_sanctions["stateSanctions"] \
            = aggregated_state_sanctions.state.apply(lambda x: {"state": x})

        aggregated_state_sanctions.drop(columns=["state"], inplace=True)

        return aggregated_state_sanctions

    @classmethod
    def _merge_sanctions(cls, aggregated_non_state_sanctions, aggregated_state_sanctions):
        merge_columns = column.SANCTIONS_COLUMNS+column.SANCTION_VALUE_COLUMNS

        aggregated_sanctions = aggregated_state_sanctions.merge(
            aggregated_non_state_sanctions,
            on="ENTITY_ID",
            how="outer"
        )

        aggregated_sanctions = cls._fill_null_non_state_sanctions(aggregated_sanctions)

        aggregated_sanctions = cls._fill_null_state_sanctions(aggregated_sanctions)

        aggregated_sanctions["sanctions"] = aggregated_sanctions[merge_columns].to_json(orient="records")

        aggregated_sanctions.drop(columns=merge_columns, inplace=True)

        aggregated_sanctions.rename(columns={"ENTITY_ID": "entityId"}, inplace=True)

        return aggregated_sanctions

    @classmethod
    def _fill_null_non_state_sanctions(cls, aggregated_sanctions):
        non_state_columns = [c for c in column.SANCTIONS_COLUMNS if c not in ("federalSanctions", "stateSanctions")]
        value_columns = [c for c in aggregated_sanctions.columns.values if c.endswith("Value")]

        aggregated_sanctions[non_state_columns] = aggregated_sanctions[non_state_columns].fillna("N")

        aggregated_sanctions[value_columns] = aggregated_sanctions[value_columns].fillna(
            "NO ACTIONS REPORTED AT THIS TIME"
        )

        return aggregated_sanctions

    @classmethod
    def _fill_null_state_sanctions(cls, aggregated_sanctions):
        aggregated_sanctions.loc[aggregated_sanctions.stateSanctions.isnull(), "stateSanctions"] = \
            aggregated_sanctions.loc[aggregated_sanctions.stateSanctions.isnull(), "stateSanctions"].apply(
                lambda x: {"state": []}
            )

        aggregated_sanctions["stateSanctionsValue"] = aggregated_sanctions["stateSanctionsValue"].fillna(
            "NO ACTIONS REPORTED AT THIS TIME"
        )

        return aggregated_sanctions

    @classmethod
    def _aggregate_sanction(cls, aggregated_sanctions, sanctions, board_code, column_name):
        sanction = sanctions[sanctions.BOARD_CD == board_code].copy()

        sanction[column_name] = "Y"

        sanction[f"{column_name}Value"] = "ACTION_REPORTED"

        aggregated_sanctions = aggregated_sanctions.merge(sanction, how="left", on="ENTITY_ID")

        return aggregated_sanctions.drop(columns=["BOARD_CD_x", "BOARD_CD_y"], errors="ignore")

    @classmethod
    def _fill_null_sanctions(cls, ama_masterfile):
        null_sanctions = {key:"N" for key in column.SANCTIONS_COLUMNS}

        null_sanctions.update(
            {f"{key}Value":"NO ACTIONS REPORTED AT THIS TIME" for key in column.SANCTIONS_COLUMNS}
        )

        null_sanctions["stateSanctions"] = {"state": []}

        ama_masterfile.sanctions[ama_masterfile.sanctions.isna()] = [null_sanctions]

        return ama_masterfile

    @classmethod
    def _pickle_masterfile(cls, ama_masterfile):
        ama_masterfile.loc[:, "sanctions"] = ama_masterfile.loc[:, "sanctions"].apply(pickle.dumps)

        return ama_masterfile


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class AMAProfileTransformerParameters:
    execution_time: str = None


class AMAProfileTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = AMAProfileTransformerParameters

    def run(self):
        LOGGER.info("Reading physician profile PSV files...")

        dataframes = [self._csv_to_dataframe(input_file) for input_file in self._data]
        ama_masterfile = dataframes[0]
        for dataframe in dataframes[1:]:
            ama_masterfile = ama_masterfile.merge(dataframe, on="entityId", how="left")

        LOGGER.info("Writing ama_masterfile table Feather file...")
        return [self._dataframe_to_csv(ama_masterfile)]


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

        qldb_profiles = self._create_vericre_profile_from_caqh_profile(profiles, current_date)

        return [json.dumps(qldb_profiles).encode()]

    def _create_vericre_profile_from_caqh_profile(self, profiles, current_date):
        return [self._create_qldb_profile(profile, current_date) for profile in profiles]

    def _create_qldb_profile(self, raw_profile, current_date):
        profile = xmltodict.parse(raw_profile)['Provider']

        transformed_profile = {
            'FutureBoardExamDate': self._create_future_board_exam_date(profile["Specialty"]),
            'TaxID': self._create_tax_id(profile["Practice"]["Tax"]),
            'WorkHistory': self._create_work_history(profile["WorkHistory"]),
            'FirstName': profile.get("FirstName"),
            'OtherName': self._create_other_name(profile["OtherName"]),
            'PreviousInsurance': self._create_previous_insurance(profile["Insurance"], current_date),
            'Languages': self._create_languages(profile["Language"]),
            'ProviderMedicaid': self._create_provider_medicaid(profile["ProviderMedicare"]),
            'TimeGap': self._create_time_gap(profile["TimeGap"]),
            'SSN': profile.get("SSN"),
            'MedicareProviderFlag': profile.get("MedicareProviderFlag"),
            'OtherNameFlag': profile.get("OtherNameFlag"),
            'ProviderMedicare': profile.get("ProviderMedicare"),
            'Insurance': self._create_insurance(profile["Insurance"], current_date),
            'MedicaidProviderFlag': profile.get("MedicaidProviderFlag"),
            'ProviderAddress': self._create_provider_address(profile["ProviderAddress"]),
            'ProviderCDS': self._create_provider_cds(profile["ProviderCDS"]),
            'LastName': profile.get("LastName"),
            'ProviderType': profile.get("ProviderType"),
            'ECFMGIssueDate': profile.get("ECFMGIssueDate")
        }

        return transformed_profile

    @classmethod
    def _create_future_board_exam_date(cls, specialties):
        future_board_exam_date = ''

        for specialty in specialties:
            if specialty["SpecialtyType"]["SpecialtyTypeDescription"] == "Primary":
                if "FutureBoardExamDate" in specialty:
                    future_board_exam_date = specialty["FutureBoardExamDate"]

        return future_board_exam_date

    @classmethod
    def _create_tax_id(cls, taxes):
        tax_id = ""

        for tax in taxes:
            if tax.get("TaxType", {}).get("TaxTypeDescription") == "Individual":
                tax_id = tax.get("TaxID", "")
                break

        return tax_id

    @classmethod
    def _create_work_history(cls, work_histories):
        for work_history in work_histories:
            work_history.pop("@ID")

        return sorted(work_histories, key=lambda x: x["StartDate"])

    @classmethod
    def _create_other_name(cls, other_name):
        other_name.pop("@ID")

        return other_name

    @classmethod
    def _create_previous_insurance(cls, insurances, current_date):
        for insurance in insurances:
            insurance.pop("@ID")

        previous_insurances = [
            insurance for insurance in insurances
            if datetime.fromisoformat(insurance["EndDate"]) <= current_date
        ]

        return sorted(previous_insurances, key=lambda x: x["StartDate"])

    @classmethod
    def _create_languages(cls, languages):
        return [lang["Language"]["LanguageName"] for lang in languages]

    @classmethod
    def _create_provider_medicaid(cls, provider_medicare):
        provider_medicare.pop("@ID")

        return provider_medicare

    @classmethod
    def _create_time_gap(cls, time_gaps):
        for time_gap in time_gaps:
            time_gap.pop("@ID")

        time_gaps = [time_gap for time_gap in time_gaps if time_gap["GapExplanation"] != "Academic/Training leave"]

        return sorted(time_gaps, key=lambda x: x["StartDate"])

    @classmethod
    def _create_insurance(cls, insurances, current_date):
        insurances = [
            insurance for insurance in insurances
            if datetime.fromisoformat(insurance["EndDate"]) > current_date
        ]

        return sorted(insurances, key=lambda x: x["StartDate"])

    @classmethod
    def _create_provider_address(cls, provider_address):
        provider_address.pop("@ID")

        return provider_address

    @classmethod
    def _create_provider_cds(cls, all_provider_cds):
        if isinstance(all_provider_cds, dict):
            all_provider_cds = [all_provider_cds]

        for provider_cds in all_provider_cds:
            provider_cds.pop("@ID")
        modified_all_provider_cds = sorted(all_provider_cds, key=lambda x: x["IssueDate"])

        return modified_all_provider_cds


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class FeatherSplitTransformerParameters:
    split_count: str = None
    execution_time: str = None


class FeatherSplitTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = FeatherSplitTransformerParameters

    def run(self):
        split_count = int(self._parameters.split_count) if self._parameters.split_count else 1
        ama_masterfile = self._feather_to_dataframe(self._data[0])

        LOGGER.info("Generating %d Feather files...", split_count)
        return [self._dataframe_to_csv(x) for x in numpy.array_split(ama_masterfile, split_count)]


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class JSONTransformerParameters:
    split_count: str = None
    execution_time: str = None


class JSONTransformerTask(CSVReaderMixin, Task):
    PARAMETER_CLASS = JSONTransformerParameters

    def run(self):
        split_count = int(self._parameters.split_count) if self._parameters.split_count else 1
        ama_masterfile = self._csv_to_dataframe(self._data[0])

        # LOGGER.info("Unpickling column values...")
        # for column_name in column.AGGREGATED_COLUMNS:
        #     ama_masterfile.loc[:, column_name] = ama_masterfile.loc[:, column_name].apply(pickle.loads)

        LOGGER.info("Generating %d JSON files...", split_count)
        return [x.to_json(orient="records").encode() for x in numpy.array_split(ama_masterfile, split_count)]
