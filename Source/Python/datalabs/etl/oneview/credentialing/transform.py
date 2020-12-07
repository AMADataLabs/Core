"""Oneview Credentialing Table Columns"""

import logging
import pandas

from   datalabs.etl.oneview.credentialing.column import customer_columns, product_columns, order_columns, customer_addresses_columns
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class CredentialingTransformerTask(TransformerTask):
    def _get_columns(self):
        return [customer_columns, product_columns, order_columns]


class CredentialingFinalTransformerTask(TransformerTask):
    def _transform(self):
        dataframes = [self._dataframe_to_csv(csv) for csv in self._parameters.data]
        merged_dataframes = [self._merge_dataframes(dataframes)]

        return merged_dataframes

    def _merge_dataframes(self, dataframes):
        new_df = pandas.merge(dataframes[1], dataframes[0], on='number')
        return [new_df, dataframes[2], dataframes[3]]

    def _get_columns(self):
        return [customer_columns, product_columns, order_columns, customer_addresses_columns]