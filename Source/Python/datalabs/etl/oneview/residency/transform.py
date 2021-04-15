""" Oneview Residency Transformer"""
from   io import BytesIO
import logging
import pandas

from   datalabs.etl.oneview.residency.column import PROGRAM_COLUMNS, MEMBER_COLUMNS, INSTITUTION_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ResidencyTransformerTask(TransformerTask):
    def _to_dataframe(self):
        df_data = [pandas.read_csv(BytesIO(data), sep='|', error_bad_lines=False, encoding='latin', low_memory=False)
                   for data in self._parameters['data']]
        new_dataframes = [self._merge_dataframe(df) for df in df_data]

        return new_dataframes

    @classmethod
    def _merge_dataframe(cls, dataframes):
        dataframes[0] = dataframes[0].loc[(dataframes[0]['pgm_activity_code'] == 0)].reset_index(drop=True)
        dataframes[1].pgm_id = dataframes[1].pgm_id.astype(str)
        dataframes[2].pgm_id = dataframes[2].pgm_id.astype(str)

        dataframes[1] = dataframes[1].loc[(dataframes[1]['addr_type'] == 'D')].reset_index(drop=True)
        dataframes[3] = dataframes[3].loc[(dataframes[3]['affiliation_type'] == 'S')].reset_index(drop=True)

        merged_df = pandas.merge(dataframes[0], dataframes[1], on='pgm_id')
        merged_df = pandas.merge(merged_df, dataframes[3], on='pgm_id')

        LOGGER.info(dataframes)
        return [merged_df, dataframes[2], dataframes[3]]

    def _get_columns(self):
        return [PROGRAM_COLUMNS, MEMBER_COLUMNS, INSTITUTION_COLUMNS]
