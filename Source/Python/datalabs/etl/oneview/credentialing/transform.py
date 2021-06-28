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
    def _csv_to_dataframe(self, data):
        main_dataframe = pandas.read_csv(BytesIO(data[1]), encoding='latin-1')

        address_dataframe = pandas.read_excel(BytesIO(data[0]))

        return [address_dataframe, main_dataframe]

    def _preprocess_data(self, data):
        credentialing_main = data[1].rename(columns={'CUSTOMER_NBR': 'number'})
        new_df = credentialing_main.merge(data[0], how='left', on='number')
        return [new_df]

    def _get_columns(self):
        return [columns.CUSTOMER_ADDRESSES_COLUMNS]
