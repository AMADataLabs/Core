""" Oneview PPD Transformer"""
import logging

import pandas

from   datalabs.etl.oneview.ppd.column import NPI_COLUMNS, PPD_COLUMNS, MEDICAL_STUDENT_COLUMNS, PHYSICIAN_COLUMNS

from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


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
        medical_education_number_table = npi_data.loc[npi_data['KEY_TYPE_ID'] == '18']

        return medical_education_number_table[['PARTY_ID', 'KEY_VAL']].rename(columns={'KEY_VAL': 'meNumber'})

    @classmethod
    def _create_npi_table(cls, npi_data):
        npi = npi_data.loc[npi_data['KEY_TYPE_ID'] == '38']

        return npi[['PARTY_ID', 'KEY_VAL']].rename(columns={'KEY_VAL': 'npi'})

    @classmethod
    def _create_entity_table(cls, npi_data):
        entity_data = npi_data.loc[npi_data['KEY_TYPE_ID'] == '9']

        return entity_data[['PARTY_ID', 'KEY_VAL']].rename(columns={'KEY_VAL': 'entity_id'})

    # pylint: disable=too-many-arguments
    @classmethod
    def _merge_data(cls, medical_education_number_table, npi_table, entity_table):
        merged_npi_me = medical_education_number_table.merge(npi_table, on='PARTY_ID', how="left").drop_duplicates()
        merged_npi_entity_me = merged_npi_me.merge(entity_table, on='PARTY_ID', how="left", sort=True).drop_duplicates()

        merged_npi_entity_me['meNumber'] = merged_npi_entity_me['meNumber'].str.lstrip('0')

        return merged_npi_entity_me

    def _get_columns(self):
        return [NPI_COLUMNS]


class PPDTransformerTask(TransformerTask):
    def _csv_to_dataframe(self, data: bytes, on_disk, **kwargs) -> pandas.DataFrame:
        return super()._csv_to_dataframe(data, on_disk, sep='|', **kwargs)

    def _preprocess_data(self, data):
        ppd, race_ethnicity, medical_student = data
        LOGGER.debug('PPD Table: %s', ppd)
        LOGGER.debug('Race/Ethnicity Table: %s', race_ethnicity)
        LOGGER.debug('Medical Student Table: %s', medical_student)

        ppd.meNumber = ppd.meNumber.astype(str)
        race_ethnicity.medical_education_number = race_ethnicity.medical_education_number.astype(str)

        race_ethnicity_table = self.create_race_ethnicity_table(race_ethnicity)
        medical_student_table = self.create_medical_student_table(medical_student)

        transformed_ppd = self._merge_data(ppd, race_ethnicity_table, medical_student_table, )

        ########## REMOVE AFTER DATA SOURCE FIXED###########
        transformed_ppd['PDRP_flag'] = 'filler'
        ####################################################

        final_ppd = self._add_person_type(transformed_ppd)

        return [final_ppd]

    @classmethod
    def create_race_ethnicity_table(cls, race_ethnicity_data):
        return race_ethnicity_data[['medical_education_number', 'race_ethnicity']].rename(
            columns={'medical_education_number': 'meNumber'})

    @classmethod
    def create_medical_student_table(cls, medical_student_data):
        medical_student_data = medical_student_data.rename(columns=MEDICAL_STUDENT_COLUMNS)
        medical_student_data['person_type'] = 'Student'

        return medical_student_data

    # pylint: disable=too-many-arguments
    @classmethod
    def _merge_data(cls, ppd, race_ethnicity, medical_student):
        LOGGER.debug('Race/Ethnicity Table: %s', race_ethnicity)
        LOGGER.debug('Medical Student Table: %s', medical_student)
        merged_ppd_race_ethnicity = ppd.merge(
            race_ethnicity, on='meNumber', how="left", sort=True).drop_duplicates()

        LOGGER.debug('PPD Table w/ Race/Ethnicity: %s', merged_ppd_race_ethnicity)

        merged_ppd_race_ethnicity_with_type = cls._add_person_type(merged_ppd_race_ethnicity)
        merged_ppd_student_data = merged_ppd_race_ethnicity_with_type.append(medical_student, ignore_index=True)

        LOGGER.debug('PPD Table w/ Students: %s', merged_ppd_student_data)

        return merged_ppd_student_data

    @classmethod
    def _add_person_type(cls, data):
        person_type = []

        for row in data['topCode'].to_list():
            if row == '012':
                person_type.append('Resident')
            else:
                person_type.append('Physician')

        data['person_type'] = person_type

        return data

    def _get_columns(self):
        return [PPD_COLUMNS]


class PhysicianTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        ppd, npi, membership = data

        physician = self._merge_data(ppd, npi, membership)

        return [physician]

    # pylint: disable=too-many-arguments
    @classmethod
    def _merge_data(cls, ppd_table, npi_table, membership):
        ppd_npi = ppd_table.merge(npi_table, on='meNumber', how="left").drop_duplicates()

        membership = membership.rename(columns={'PARTY_ID_FROM': 'PARTY_ID', 'DESC': 'MEMBERSHIP_STATUS'})
        ppd_membership = ppd_npi.merge(membership['PARTY_ID', 'MEMBERSHIP_STATUS'],
                                       on='PARTY_ID', how="left").drop_duplicates(ignore_index=True)

        return ppd_membership

    def _get_columns(self):
        return [PHYSICIAN_COLUMNS]
