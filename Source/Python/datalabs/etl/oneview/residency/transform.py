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
        new_dataframes = self._transform_dataframes(df_data)

        return new_dataframes

    def _transform_dataframes(cls, dataframes):
        dataframes[1].pgm_id = dataframes[1].pgm_id.astype(str)
        dataframes[2].pgm_id = dataframes[2].pgm_id.astype(str)
        dataframes[3].ins_id = dataframes[3].ins_id.astype(str)
        dataframes[4].ins_id = dataframes[4].ins_id.astype(str)

        dataframes[0] = dataframes[0].loc[(dataframes[0]['pgm_activity_code'] == '0')].reset_index(drop=True)
        dataframes[1] = dataframes[1].loc[(dataframes[1]['addr_type'] == 'D')].reset_index(drop=True)
        dataframes[3] = dataframes[3].loc[(dataframes[3]['affiliation_type'] == 'S')].reset_index(drop=True)

        program_information = pandas.merge(dataframes[0], dataframes[1], on='pgm_id')
        program_information = pandas.merge(program_information, dataframes[3], on='pgm_id')

        program_institution = pandas.merge(dataframes[3], dataframes[4], on='ins_id')

        program_personnel_member = dataframes[2]
        primary_keys = [column['pgm_id'] + column['aamc_id']
                        for index, column in program_personnel_member.iterrows()]
        program_personnel_member['id'] = primary_keys

        return [program_information, program_personnel_member, program_institution]

    def _get_columns(self):
        return [PROGRAM_COLUMNS, MEMBER_COLUMNS, INSTITUTION_COLUMNS]
