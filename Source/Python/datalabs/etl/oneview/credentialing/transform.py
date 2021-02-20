"""Oneview Credentialing Table Columns"""
from   io import BytesIO
import logging
import pandas

from   datalabs.etl.oneview.credentialing.column import \
    CUSTOMER_COLUMNS, PRODUCT_COLUMNS, ORDER_COLUMNS, CUSTOMER_ADDRESSES_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class CredentialingTransformerTask(TransformerTask):
    def _get_columns(self):
        return [CUSTOMER_COLUMNS, PRODUCT_COLUMNS, ORDER_COLUMNS]


class CredentialingFinalTransformerTask(TransformerTask):
    def _transform(self):
        dataframes = self._to_dataframe(self._parameters['data'])
        self._parameters['data'] = self._merge_dataframes(dataframes)

        data = super()._transform()

        return data

    @classmethod
    def _to_dataframe(cls, data):
        main_dataframe = pandas.read_csv(BytesIO(data[1]))
        address_dataframe = pandas.read_excel(BytesIO(data[0]))
        return [address_dataframe, main_dataframe]

    @classmethod
    def _merge_dataframes(cls, dataframes):
        new_df = dataframes[1].merge(dataframes[0], how='left', on='number')
        return [new_df]

    def _get_columns(self):
        return [CUSTOMER_ADDRESSES_COLUMNS]
