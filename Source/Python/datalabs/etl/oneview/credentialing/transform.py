"""Oneview Credentialing Table Columns"""

import logging
import os
import pandas

from   datalabs.etl.task import ETLException
from   datalabs.etl.oneview.credentialing.column import customer_columns, product_columns, order_columns
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class CredentialingTransformer(TransformerTask):
    def _transform(self):
        LOGGER.info(self._parameters.data)
        try:
            selected_data = self._select_columns(self._parameters.data)
            renamed_data = self._rename_columns(selected_data)
            merged_data = self._merge_data(renamed_data)
            csv_data = [self._dataframe_to_csv(data) for data in merged_data]

        except Exception as exception:
            raise ETLException("Invalid data") from exception

        return csv_data

    def _get_columns(self):
        return [customer_columns, product_columns, order_columns]

    def _merge_data(self, data):
        address_file = self._parameters.variables['CREDENTIALINGADDRESS']
        addresses = pandas.read_excel(address_file,
                                      usecols=['number', 'company_name', 'street_one', 'street_two', 'street_three',
                                               'city', 'state', 'zipcode', 'phone_number'])
        addresses.columns = ['number', 'company_name', 'address_1', 'address_2', 'address_3', 'city', 'state',
                             'zipcode', 'phone_number']
        data[0].number = data[0].number.astype("int64")
        data[0] = pandas.merge(data[0], addresses, on='number', how='left')

        return data
