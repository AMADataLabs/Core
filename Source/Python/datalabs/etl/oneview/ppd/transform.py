""" Oneview PPD Transformer"""
import logging
import pandas

from   datalabs.etl.oneview.ppd.column import PPD_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class PPDTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        npi_table = data[1]
        ppd_table = data[0]

        ppd_table.ME_NUMBER = ppd_table.ME_NUMBER.astype(str)

        medical_education_number_table = self._create_medical_education_number_table(npi_table)
        npi_table = self._create_npi_table(npi_table)
        entity_table = self._create_entity_table(npi_table)

        transformed_ppd = self.merge_dataframes(medical_education_number_table, npi_table, entity_table, ppd_table)

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
    def _merge_dataframes(cls, medical_education_number, npi_table, entity_table, ppd_table):
        merged_npi_me = pandas.merge(medical_education_number, npi_table, on='PARTY_ID', how="left").drop_duplicates()
        merged_npi_entity_me = pandas.merge(merged_npi_me, entity_table, on='PARTY_ID', how="left").drop_duplicates()

        return pandas.merge(ppd_table, merged_npi_entity_me, on='ME_NUMBER', how="left").drop_duplicates()

    def _get_columns(self):
        return [PPD_COLUMNS]
