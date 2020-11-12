""" Oneview Residency Transformer"""
import logging
import pandas

from   datalabs.etl.oneview.residency.column import program_columns, member_columns, institution_columns
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ResidencyTransformer(TransformerTask):
    def _transform(self):
        self._parameters.data = self._merge_dataframe()
        data = super()._transform()

        return data

    def _merge_dataframe(self):
        self._parameters.data[1].pgm_id = self._parameters.data[1].pgm_id.astype(str)
        new_df = pandas.merge(self._parameters.data[0], self._parameters.data[1], on='pgm_id')
        return [new_df, self._parameters.data[2], self._parameters.data[3]]

    def _get_columns(self):
        return [program_columns, member_columns, institution_columns]
