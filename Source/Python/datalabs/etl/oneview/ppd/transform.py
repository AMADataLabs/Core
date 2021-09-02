""" Oneview PPD Transformer"""
import dask.dataframe
import logging

from   datalabs.etl.oneview.ppd.column import PPD_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class PPDTransformerTask(TransformerTask):
    def _csv_to_dataframe(self, path: str, **kwargs) -> dask.dataframe:
        return dask.dataframe.read_csv(path, sep='|', dtype=str, **kwargs)

    def _preprocess_data(self, data):
        npi = data[1]
        ppd = data[0]
        race_ethnicity = data[2]
        medical_student = data[3]

        ppd.ME_NUMBER = ppd.ME_NUMBER.astype(str)
        race_ethnicity.medical_education_number = race_ethnicity.medical_education_number.astype(str)

        medical_education_number_table = self._create_medical_education_number_table(npi)
        npi_table = self._create_npi_table(npi)
        entity_table = self._create_entity_table(npi)
        race_ethnicity_table = self.create_race_ethnicity_table(race_ethnicity)
        medical_student_table = self.create_medical_student_table(medical_student)

        transformed_ppd = self._merge_dataframes(medical_education_number_table, npi_table, entity_table,
                                                 race_ethnicity_table, medical_student_table, ppd)

        return [transformed_ppd]

    @classmethod
    def _create_medical_education_number_table(cls, npi_data):
        medical_education_number = npi_data.loc[npi_data['KEY_TYPE_ID'] == 18]

        return medical_education_number[['PARTY_ID', 'KEY_VAL']].rename(columns={'KEY_VAL': 'ME_NUMBER'})

    @classmethod
    def _create_npi_table(cls, npi_data):
        npi = npi_data.loc[npi_data['KEY_TYPE_ID'] == 38]

        return npi[['PARTY_ID', 'KEY_VAL']].rename(columns={'KEY_VAL': 'npi'})

    @classmethod
    def _create_entity_table(cls, npi_data):
        entity_data = npi_data.loc[npi_data['KEY_TYPE_ID'] == 9]

        return entity_data[['PARTY_ID', 'KEY_VAL']].rename(columns={'KEY_VAL': 'entity_id'})

    @classmethod
    def create_race_ethnicity_table(cls, race_ethnicity_data):
        return race_ethnicity_data[['medical_education_number', 'race_ethnicity']].rename(
            columns={'medical_education_number': 'ME_NUMBER'})

    @classmethod
    def create_medical_student_table(cls, medical_student_data):
        return medical_student_data.rename(columns={'me_no': 'ME_NUMBER',
                                                    'mailing_name': 'MAILING_NAME',
                                                    'last_name': 'LAST_NAME',
                                                    'first_name': 'FIRST_NAME',
                                                    'middle_name': 'MIDDLE_NAME',
                                                    'suffix': 'SUFFIX_CODE',
                                                    'mail_line_1': 'PREFERRED_ADDR1',
                                                    'mail_line_2': 'PREFERRED_ADDR2',
                                                    'state': 'PREFERRED_STATE',
                                                    'zipcode': 'PREFERRED_ZIP',
                                                    'sector': 'PREFERRED_PLUS4',
                                                    'addr_city': 'PREFERRED_CITY',
                                                    'carrier_route': 'PREFERRED_CARRIERROUTE',
                                                    'addr_undeliver_flg': 'UNDELIVER_FLAG',
                                                    'fips_county': 'FIPS_COUNTY',
                                                    'fips_state': 'FIPS_STATE',
                                                    'region': 'REGION',
                                                    'msa_population_size': 'MSA_POPULATION',
                                                    'division': 'DIVISION',
                                                    'group': 'GROUP',
                                                    'tract': 'TRACT',
                                                    'census_suffix': 'SUFFIX',
                                                    'block_group': 'BLOCK_GROUP',
                                                    'metro_micro_indicator': '',
                                                    'cbsa': 'CBSA',
                                                    'cbsa_division_indicator': 'MICRO_METRO_IND',
                                                    'school_name': 'GRADSCHOOLCODE',
                                                    'school_state': 'GRADSCHOOLSTATE',
                                                    'grad_year': 'GRADYEAR',
                                                    'birth_year': 'BIRTH_YEAR',
                                                    'birth_city': 'BIRTH_CITY',
                                                    'birth_state': 'BIRTH_STATE',
                                                    'birth_country': 'BIRTH_COUNTRY',
                                                    'gender': 'GENDER',
                                                    'addr_type_ind': 'ADDRESS_TYPE',
                                                    'phone_no': 'PREFERREDPHONENUMBER',
                                                    'presumed_dead': 'PENDINGDEAD_IND',
                                                    'contact_flg': 'NOCONTACT_IND'
                                                    }
                                           )

    # pylint: disable=too-many-arguments
    @classmethod
    def _merge_dataframes(cls, medical_education_number, npi_table, entity_table, race_and_ethnicity,
                          medical_student, ppd_table):
        merged_npi_me = medical_education_number.merge(npi_table, on='PARTY_ID', how="left").drop_duplicates()
        merged_npi_entity_me = merged_npi_me.merge(entity_table, on='PARTY_ID', how="left").drop_duplicates()

        merged_npi_entity_me['ME_NUMBER'] = merged_npi_entity_me['ME_NUMBER'].str.lstrip('0')

        merged_ppd = ppd_table.merge(merged_npi_entity_me, on='ME_NUMBER', how="left").drop_duplicates()
        merged_ppd_race_ethnicity = merged_ppd.merge(race_and_ethnicity, on='ME_NUMBER', how="left").drop_duplicates()

        merged_ppd_student_data = merged_ppd_race_ethnicity.append(medical_student, ignore_index=True)

        return merged_ppd_student_data

    def _get_columns(self):
        return [PPD_COLUMNS]
