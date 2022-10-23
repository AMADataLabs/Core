""" Oneview PPD Transformer"""
import logging

import pandas

from   datalabs.etl.oneview.ppd.column import NPI_COLUMNS, PPD_COLUMNS, MEDICAL_STUDENT_COLUMNS, PHYSICIAN_COLUMNS

from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class NPITransformerTask(TransformerTask):
    def _preprocess(self, dataset):
        party_keys = dataset[0]

        medical_education_numbers = self._extract_medical_education_numbers(party_keys)

        national_provider_identifiers = self._extract_national_provider_identifiers(party_keys)

        entities = self._extract_entities(party_keys)

        me_npi_entity_map = self._merge(medical_education_numbers, national_provider_identifiers, entities)

        return [me_npi_entity_map]

    @classmethod
    def _extract_medical_education_numbers(cls, party_keys):
        medical_education_numbers = party_keys.loc[party_keys['KEY_TYPE_ID'] == '18']

        return medical_education_numbers[['PARTY_ID', 'KEY_VAL']].rename(columns={'KEY_VAL': 'meNumber'})

    @classmethod
    def _extract_national_provider_identifiers(cls, party_keys):
        npi = party_keys.loc[party_keys['KEY_TYPE_ID'] == '38']

        return npi[['PARTY_ID', 'KEY_VAL']].rename(columns={'KEY_VAL': 'npi'})

    @classmethod
    def _extract_entities(cls, party_keys):
        entities = party_keys.loc[party_keys['KEY_TYPE_ID'] == '9']

        return entities[['PARTY_ID', 'KEY_VAL']].rename(columns={'KEY_VAL': 'entity_id'})

    # pylint: disable=too-many-arguments
    @classmethod
    def _merge(cls, medical_education_numbers, national_provider_identifiers, entities):
        me_npi = medical_education_numbers.merge(
            national_provider_identifiers,
            on='PARTY_ID',
            how="left"
        ).drop_duplicates()

        mp_npi_entity = me_npi.merge(entities, on='PARTY_ID', how="left", sort=True).drop_duplicates()

        return mp_npi_entity

    def _get_columns(self):
        return [NPI_COLUMNS]


class PPDTransformerTask(TransformerTask):
    def _parse(self, dataset):
        encoding = ["utf8", "utf8", "cp1252"]

        return [self._csv_to_dataframe(data, sep='|', encoding=encoding) for data, encoding in zip(dataset, encoding)]

    def _preprocess(self, dataset):
        ppd, race_ethnicity, medical_student = dataset
        LOGGER.debug('PPD Table: %s', ppd)
        LOGGER.debug('Race/Ethnicity Table: %s', race_ethnicity)
        LOGGER.debug('Medical Student Table: %s', medical_student)

        ppd.meNumber = ppd.meNumber.astype(str)
        race_ethnicity.medical_education_number = race_ethnicity.medical_education_number.astype(str)

        race_ethnicities = self._clean_race_ethnicities(race_ethnicity)

        medical_students = self._clean_medical_students(medical_student)

        transformed_ppd = self._supplement_ppd(ppd, medical_students, race_ethnicities)

        transformed_ppd = self._convert_no_release_indicator_to_boolean(transformed_ppd)

        ########## REMOVE AFTER DATA SOURCE FIXED ##########
        transformed_ppd['PDRP_flag'] = 'filler'
        ####################################################

        final_ppd = self._add_person_type(transformed_ppd)

        return [final_ppd]

    @classmethod
    def _clean_race_ethnicities(cls, race_ethnicity_data):
        return race_ethnicity_data[['medical_education_number', 'race_ethnicity']].rename(
            columns={'medical_education_number': 'meNumber'}
        )

    @classmethod
    def _clean_medical_students(cls, medical_student_data):
        medical_student_data = medical_student_data.rename(columns=MEDICAL_STUDENT_COLUMNS)
        medical_student_data['topCode'] = '000'

        return medical_student_data

    # pylint: disable=too-many-arguments
    @classmethod
    def _supplement_ppd(cls, ppd, medical_students, race_ethnicities):
        ppd_student = ppd.append(medical_students, ignore_index=True)
        LOGGER.debug('Race/Ethnicity Table: %s', race_ethnicities)
        LOGGER.debug('Medical Student Table: %s', medical_students)
        LOGGER.debug('PPD Table w/ Students: %s', ppd_student)

        ppd_student_race = ppd_student.merge(race_ethnicities, on='meNumber', how="left", sort=True)
        ppd_student_race = ppd_student_race.drop_duplicates()

        LOGGER.debug('PPD Table w/ Race/Ethnicity: %s', ppd_student_race)

        ppd_student_race_type = cls._add_person_type(ppd_student_race)

        return ppd_student_race_type

    @classmethod
    def _add_person_type(cls, supplemented_ppd):
        person_type = []

        for row in supplemented_ppd.topCode.to_list():
            if row == '012':
                person_type.append('Resident')
            elif row == '000':
                person_type.append('Student')
            else:
                person_type.append('Physician')

        supplemented_ppd['person_type'] = person_type

        return supplemented_ppd

    @classmethod
    def _convert_no_release_indicator_to_boolean(cls, ppd):
        ppd['no_release_ind'] = ppd.no_release_ind == 'Y'

        return ppd

    def _get_columns(self):
        return [PPD_COLUMNS]


class PhysicianTransformerTask(TransformerTask):
    # pylint: disable=no-self-use
    def _preprocess(self, dataset):
        ppd, npi, membership, email_status = dataset

        physician = self._merge(ppd, npi, membership, email_status)

        physician = self._drop_no_release_physicians(physician)

        return [physician]

    def _get_columns(self):
        return [PHYSICIAN_COLUMNS]

    def _postprocess(self, dataset):
        physician = dataset[0]

        filled_physician = self._fill_defaults(physician)

        cleaned_physician = self._clean_physician(filled_physician)

        return [cleaned_physician]

    # pylint: disable=too-many-arguments
    @classmethod
    def _merge(cls, ppd, npi, membership, email_status):
        ppd_npi = cls._merge_npi(ppd, npi)

        ppd_membership = cls._merge_membership(ppd_npi, membership)

        ppd_email_status = cls._merge_email_status(ppd_membership, email_status)

        return ppd_email_status

    @classmethod
    def _drop_no_release_physicians(cls, physician):
        physician = physician[physician.no_release_ind != 'True']

        return physician

    @classmethod
    def _fill_defaults(cls, physician):
        physician.federal_information_processing_standard_state.fillna('  ', inplace=True)
        physician.federal_information_processing_standard_county.fillna('   ', inplace=True)
        physician.core_based_statistical_area.fillna('00000', inplace=True)
        physician.type_of_practice.fillna('100', inplace=True)
        physician.present_employment.fillna('110', inplace=True)
        physician.primary_specialty.fillna('000', inplace=True)
        physician.secondary_specialty.fillna('000', inplace=True)
        physician.major_professional_activity.fillna('NCL', inplace=True)

        return physician

    @classmethod
    def _clean_physician(cls, physician):
        cls._fix_pohnpei_fips_county_code(physician)

        physician.federal_information_processing_standard_state[
            (physician.federal_information_processing_standard_state == '02') & \
            (physician.federal_information_processing_standard_county == '066')
        ] = '  '
        physician.federal_information_processing_standard_county[
            (physician.federal_information_processing_standard_state == '  ') & \
            (physician.federal_information_processing_standard_county == '066')
        ] = '   '

        cls._consolidate_duplicates(physician)

        return physician

    @classmethod
    def _merge_npi(cls, ppd, npi):
        return ppd.merge(npi, on='meNumber', how="left").drop_duplicates()

    @classmethod
    def _merge_membership(cls, ppd, membership):
        membership = membership.rename(columns={'PARTY_ID_FROM': 'PARTY_ID', 'DESC': 'MEMBERSHIP_STATUS'})

        return ppd.merge(
            membership[['PARTY_ID', 'MEMBERSHIP_STATUS']],
            on='PARTY_ID', how="left"
        ).drop_duplicates(ignore_index=True)

    @classmethod
    def _merge_email_status(cls, ppd, email_status):
        ppd_email = ppd.merge(email_status, on='PARTY_ID', how='left').drop_duplicates(ignore_index=True)

        ppd_email.has_email.fillna(False, inplace=True)

        return ppd_email

    @classmethod
    def _fix_pohnpei_fips_county_code(cls, physician):
        physician.federal_information_processing_standard_county[
            (physician.federal_information_processing_standard_state == '64') & \
            (physician.federal_information_processing_standard_county == '003') & \
            (physician.city == 'POHNPEI')
        ] = '040'

    @classmethod
    def _consolidate_duplicates(cls, physician):
        ''' Remove duplicate records that vary only by NPI. Null NPI for the remaining record. '''
        duplicates = physician[physician.duplicated('medical_education_number')].groupby('medical_education_number')
        duplicate_me_numbers = duplicates.groups.keys()

        physician.drop_duplicates('medical_education_number', inplace=True)

        physician.national_provider_identifier[physician.medical_education_number.isin(duplicate_me_numbers)] = ''
