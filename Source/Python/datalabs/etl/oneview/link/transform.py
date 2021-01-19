""" OneView Linking Table Transformer"""
from   io import StringIO

import logging
import pandas

from   datalabs.etl.oneview.link.column import CREDENTIALING_CUSTOMER_INSTITUTION_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class CredentialingCustomerInstitution(TransformerTask):
    def _transform(self):
        dataframes = [self._to_dataframe(csv) for csv in self._parameters.data]
        self._parameters.data = [self._linking_data(df) for df in dataframes]

        return super()._transform()

    @classmethod
    def _linking_data(cls, data):
        dmatches = pandas.merge(data[0], data[1], left_on=['Street 1ST', 'City', 'State'],
                                right_on=['ins_pers_add1', 'ins_pers_city', 'ins_pers_state'])
        matches = dmatches[['Customer Number', 'ins_id']]
        return matches

    @classmethod
    def _to_dataframe(cls, file):
        return pandas.read_csv(StringIO(file))

    def _get_columns(self):
        return [CREDENTIALING_CUSTOMER_INSTITUTION_COLUMNS]
