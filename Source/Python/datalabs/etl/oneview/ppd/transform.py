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

        medical_education_number = npi_table.loc[npi_table['KEY_TYPE_ID'] == 18]
        medical_education_number = medical_education_number[['PARTY_ID', 'KEY_VAL']].rename(columns=
                                                                                            {'KEY_VAL': 'ME_NUMBER'})

        npi = npi_table.loc[npi_table['KEY_TYPE_ID'] == 38]
        npi = npi[['PARTY_ID', 'KEY_VAL']].rename(columns={'KEY_VAL': 'npi'})

        entity_id = npi_table.loc[npi_table['KEY_TYPE_ID'] == 9]
        entity_id = entity_id[['PARTY_ID', 'KEY_VAL']].rename(columns={'KEY_VAL': 'entity_id'})

        merged_npi_me = pandas.merge(medical_education_number, npi, on='PARTY_ID', how="left").drop_duplicates()
        merged_npi_entity_me = pandas.merge(merged_npi_me, entity_id, on='PARTY_ID', how="left").drop_duplicates()

        ppd_npi = pandas.merge(ppd_table, merged_npi_entity_me, on='ME_NUMBER', how="left").drop_duplicates()

        return [ppd_npi]

    def _get_columns(self):
        return [PPD_COLUMNS]
