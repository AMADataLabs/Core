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
        addresses = dataframes[1]
        addresses.pgm_id = addresses.pgm_id.astype(str)

        program_personnel_member = dataframes[2]
        program_personnel_member.pgm_id = program_personnel_member.pgm_id.astype(str)

        program_institution = dataframes[3]
        program_institution.pgm_id = program_institution.pgm_id.astype(str)
        program_institution.ins_id = program_institution.ins_id.astype(str)

        institution_info = dataframes[4]

        programs = dataframes[0].loc[(dataframes[0]['pgm_activity_code'] == '0')].reset_index(drop=True)
        addresses = addresses.loc[(addresses['addr_type'] == 'D')].reset_index(drop=True)
        program_institution = program_institution.loc[
            (program_institution['affiliation_type'] == 'S')
        ].reset_index(drop=True)
        institution_info = institution_info.loc[
            (institution_info['ins_affiliation_type'] == 'S')
        ].reset_index(drop=True)

        program_information = pandas.merge(programs, addresses, on='pgm_id')
        program_information = pandas.merge(program_information, program_institution[['pgm_id', 'ins_id']], on='pgm_id')
        institution_info = pandas.merge(institution_info, program_institution[['ins_id', 'pri_clinical_loc_ind']],
                                        on='ins_id')

        program_personnel_member = cls._generate_primary_keys(program_personnel_member)

        return [program_information, program_personnel_member, institution_info]

    @classmethod
    def _generate_primary_keys(cls, dataframe):
        primary_keys = [str(column['pgm_id']) + str(column['aamc_id'])
                        for index, column in dataframe.iterrows()]
        dataframe['id'] = primary_keys

        return dataframe

    def _get_columns(self):
        return [PROGRAM_COLUMNS, MEMBER_COLUMNS, INSTITUTION_COLUMNS]
