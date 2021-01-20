""" OneView Linking Table Transformer"""
from   io import StringIO

import logging
import pandas

from   datalabs.etl.oneview.link.column import CREDENTIALING_CUSTOMER_BUSINESS_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class CredentialingCustomerBusinessTransformerTask(TransformerTask):
    def _transform(self):
        dataframes = [self._to_dataframe(csv) for csv in self._parameters.data]
        self._parameters.data = [self._linking_data(df) for df in dataframes]

        return super()._transform()

    @classmethod
    def _linking_data(cls, data):
        data[0] = data[0].fillna('None')
        data[0]['address_1'] = [x.upper() for x in data[0]['address_1']]
        data[0]['city'] = [x.upper() for x in data[0]['city']]
        data[0]['state'] = [x.upper() for x in data[0]['state']]

        matches = pandas.merge(data[0], data[1],
                               left_on=['address_1', 'city', 'state'],
                               right_on=['physical_address_1', 'physical_city', 'physical_state'])

        return matches[['number', 'id']]

    @classmethod
    def _to_dataframe(cls, file):
        return pandas.read_csv(StringIO(file))

    def _get_columns(self):
        return [CREDENTIALING_CUSTOMER_BUSINESS_COLUMNS]
