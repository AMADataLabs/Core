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
    def _transform(self):
        LOGGER.debug(self._parameters['data'])
        table_data = [
            self._csv_to_dataframe(self._parameters['data'][0]),
            pandas.read_excel(self._parameters['data'][1], skiprows=4, dtype=str)
        ]

        preprocessed_data = self._preprocess_data(table_data)

        selected_data = self._select_columns(preprocessed_data)
        renamed_data = self._rename_columns(selected_data)

        postprocessed_data = self._postprocess_data(renamed_data)

        return [self._dataframe_to_csv(data, index=False, quoting=csv.QUOTE_NONNUMERIC) for data in postprocessed_data]

    def _preprocess_data(self, data):
        credentialing_main = data[1].rename(columns={'CUSTOMER_NBR': 'number'})
        new_df = credentialing_main.merge(data[0], how='left', on='number')
        return [new_df]

    def _get_columns(self):
        return [columns.CUSTOMER_ADDRESSES_COLUMNS]
