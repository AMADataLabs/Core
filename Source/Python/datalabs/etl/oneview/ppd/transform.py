""" Oneview PPD Transformer"""
from   io import BytesIO

import logging
import pandas

from   datalabs.etl.oneview.ppd.column import PPD_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class PPDTransformerTask(TransformerTask):
    def _to_dataframe(self):
        ppd_npi_data = [pandas.read_csv(BytesIO(file)) for file in self._parameters['data']]
        physician_data = self._merge_data(ppd_npi_data)

        return [physician_data]

    @classmethod
    def _merge_data(cls, data):
        npi_table = data[1][['PARTY_ID', 'KEY_TYPE_ID', 'KEY_VAL', 'ACTIVE_IND']]
        ppd_table = data[0]

        npi_table = npi_table.loc[npi_table['ACTIVE_IND'] == 'Y']

        medical_education_number = npi_table.loc[npi_table['KEY_TYPE_ID'] == '18']
        medical_education_number = medical_education_number[['PARTY_ID', 'KEY_VAL']].rename(columns=
                                                                                            {'KEY_VAL': 'ME_NUMBER'})

        npi = npi_table.loc[npi_table['KEY_TYPE_ID'] == '38']
        npi = npi[['PARTY_ID', 'KEY_VAL']].rename(columns={'KEY_VAL': 'npi'})

        merged_npi_me = pandas.merge(medical_education_number, npi, on='PARTY_ID', how="left").drop(columns=['PARTY_ID'])
        ppd_npi = pandas.merge(ppd_table, merged_npi_me, on='ME_NUMBER', how="left")

        return ppd_npi

    def _get_columns(self):
        return [PPD_COLUMNS]
