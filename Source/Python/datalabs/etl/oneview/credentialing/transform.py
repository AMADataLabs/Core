"""Oneview Credentialing Table Columns"""
from   io import BytesIO

import logging
import pandas

from   datalabs.etl.oneview.transform import TransformerTask

import datalabs.etl.oneview.credentialing.column as columns

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class CredentialingTransformerTask(TransformerTask):
    def _get_columns(self):
        return [columns.PRODUCT_COLUMNS, columns.ORDER_COLUMNS]


class CredentialingFinalTransformerTask(TransformerTask):
    def _to_dataframe(self):
        main_dataframe = pandas.read_csv(BytesIO(self._parameters['data'][1]))
        address_dataframe = pandas.read_excel(BytesIO(self._parameters['data'][0]))

        credentialing_data = self._merge_dataframes([address_dataframe, main_dataframe])

        return credentialing_data

    @classmethod
    def _merge_dataframes(cls, dataframes):
        credentialing_main = dataframes[1].rename(columns={'CUSTOMER_NBR': 'number'})
        new_df = credentialing_main.merge(dataframes[0], how='left', on='number')
        return [new_df]

    def _get_columns(self):
        return [columns.CUSTOMER_ADDRESSES_COLUMNS]
