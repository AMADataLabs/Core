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

    @classmethod
    def _transform_dataframes(cls, dataframes):
        addresses = dataframes[1].pgm_id.astype(str)
        program_personnel_member = dataframes[2].pgm_id.astype(str)
        program_institution = dataframes[3].ins_id.astype(str)
        institution_info = dataframes[4].ins_id.astype(str)

        programs = dataframes[0].loc[(dataframes[0]['pgm_activity_code'] == '0')].reset_index(drop=True)
        addresses = addresses.loc[(addresses['addr_type'] == 'D')].reset_index(drop=True)
        program_institution = program_institution.loc[
            (program_institution['affiliation_type'] == 'S')
        ].reset_index(drop=True)

        program_information = pandas.merge(programs, addresses, on='pgm_id')
        program_information = pandas.merge(program_information, program_institution[['pgm_id', 'ins_id']], on='pgm_id')

        institution_info = institution_info.loc[
            (institution_info['ins_affiliation_type'] == 'S')
        ].reset_index(drop=True)

        primary_keys = [column['pgm_id'] + column['aamc_id']
                        for index, column in program_personnel_member.iterrows()]
        program_personnel_member['id'] = primary_keys

        return [program_information, program_personnel_member, institution_info]

    def _get_columns(self):
        return [PROGRAM_COLUMNS, MEMBER_COLUMNS, INSTITUTION_COLUMNS]
