""" Oneview Residency Transformer"""
from   io import StringIO
import logging
import pandas

from   datalabs.etl.oneview.residency.column import PROGRAM_COLUMNS, MEMBER_COLUMNS, INSTITUTION_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ResidencyTransformerTask(TransformerTask):
    def _transform(self):
        df_data = [self._to_dataframe(data) for data in self._parameters['data']]
        self._parameters['data'] = self._merge_dataframe(df_data)
        data = super()._transform()

        return data

    @classmethod
    def _to_dataframe(cls, file):
        dataframe = pandas.read_csv(StringIO(file), sep='|', error_bad_lines=False, encoding='latin', low_memory=False)

        return dataframe

    @classmethod
    def _merge_dataframe(cls, dataframes):
        dataframes[1].pgm_id = dataframes[1].pgm_id.astype(str)
        dataframes[2].pgm_id = dataframes[2].pgm_id.astype(str)

        merged_df = pandas.merge(dataframes[0], dataframes[1], on='pgm_id')
        merged_df = pandas.merge(merged_df, dataframes[2], on='pgm_id')

        return [merged_df, dataframes[3], dataframes[4]]

    def _get_columns(self):
        return [PROGRAM_COLUMNS, MEMBER_COLUMNS, INSTITUTION_COLUMNS]
