""" Oneview PPD Transformer"""
import logging

import pandas

from   datalabs.etl.oneview.ppd.column import PHYSICIAN_COLUMNS, MEDICAL_STUDENT_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class NPITransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        npi = data[0]

        medical_education_number_table = self._create_medical_education_number_table(npi)
        npi_table = self._create_npi_table(npi)
        entity_table = self._create_entity_table(npi)

        merged_data = self._merge_data(medical_education_number_table, npi_table, entity_table)

        return [merged_data]

    @classmethod
    def _create_medical_education_number_table(cls, npi_data):
        medical_education_number_table = npi_data.loc[npi_data['KEY_TYPE_ID'] == 18]

        return medical_education_number_table[['PARTY_ID', 'KEY_VAL']].rename(columns={'KEY_VAL': 'ME_NUMBER'})

    @classmethod
    def _create_npi_table(cls, npi_data):
        npi = npi_data.loc[npi_data['KEY_TYPE_ID'] == 38]

        return npi[['PARTY_ID', 'KEY_VAL']].rename(columns={'KEY_VAL': 'npi'})

    @classmethod
    def _create_entity_table(cls, npi_data):
        entity_data = npi_data.loc[npi_data['KEY_TYPE_ID'] == 9]

        return entity_data[['PARTY_ID', 'KEY_VAL']].rename(columns={'KEY_VAL': 'entity_id'})

    # pylint: disable=too-many-arguments
    @classmethod
    def _merge_data(cls, medical_education_number_table, npi_table, entity_table):
        merged_npi_me = medical_education_number_table.merge(npi_table, on='PARTY_ID', how="left").drop_duplicates()
        merged_npi_entity_me = merged_npi_me.merge(entity_table, on='PARTY_ID', how="left", sort=True).drop_duplicates()

        merged_npi_entity_me['ME_NUMBER'] = merged_npi_entity_me['ME_NUMBER'].str.lstrip('0')

        return merged_npi_entity_me

    def _get_columns(self):
        return [{}]


class PPDTransformerTask(TransformerTask):
    def _csv_to_dataframe(self, data: bytes, on_disk, **kwargs) -> pandas.DataFrame:
        return super()._csv_to_dataframe(data, on_disk, sep='|', **kwargs)

    def _preprocess_data(self, data):
        ppd, race_ethnicity, medical_student = data

        ppd.meNumber = ppd.meNumber.astype(str)
        race_ethnicity.medical_education_number = race_ethnicity.medical_education_number.astype(str)

        race_ethnicity_table = self.create_race_ethnicity_table(race_ethnicity)
        medical_student_table = self.create_medical_student_table(medical_student)

        transformed_ppd = self._merge_data(race_ethnicity_table, medical_student_table, ppd)

        transformed_ppd['PDRP_FLAG'] = 'filler'

        return [transformed_ppd]

    @classmethod
    def create_race_ethnicity_table(cls, race_ethnicity_data):
        return race_ethnicity_data[['medical_education_number', 'race_ethnicity']].rename(
            columns={'medical_education_number': 'meNumber'})

    @classmethod
    def create_medical_student_table(cls, medical_student_data):
        return medical_student_data.rename(columns=MEDICAL_STUDENT_COLUMNS)

    # pylint: disable=too-many-arguments
    @classmethod
    def _merge_data(cls, race_and_ethnicity, medical_student, ppd_table):
        merged_ppd_race_ethnicity = ppd_table.merge(
            race_and_ethnicity, on='meNumber', how="left", sort=True).drop_duplicates()

        merged_ppd_student_data = merged_ppd_race_ethnicity.append(medical_student, ignore_index=True)

        return merged_ppd_student_data

    def _get_columns(self):
        return [{}]


class PhysicianTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        ppd, npi = data

        physician = self._merge_data(ppd, npi)

        return [physician]

    # pylint: disable=too-many-arguments
    @classmethod
    def _merge_data(cls, ppd_table, npi_table):
        return ppd_table.merge(npi_table, on='ME_NUMBER', how="left").drop_duplicates()

    def _get_columns(self):
        return [PHYSICIAN_COLUMNS]
