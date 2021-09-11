""" Oneview Residency Transformer"""
import logging
import pandas
import dask.array
import dask.dataframe

from   datalabs.etl.oneview.residency.column import PROGRAM_COLUMNS, MEMBER_COLUMNS, INSTITUTION_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ResidencyTransformerTask(TransformerTask):
    @classmethod
    def _csv_to_dataframe(cls, path, **kwargs):
        return super()._csv_to_dataframe(path, sep='|', error_bad_lines=False, encoding='latin', low_memory=False)

    # pylint: disable=too-many-arguments
    def _preprocess_data(self, data):
        programs = data[0]

        addresses = data[1]
        addresses.pgm_id = addresses.pgm_id.astype(str)

        program_personnel = data[2]
        program_personnel.pgm_id = program_personnel.pgm_id.astype(str)

        program_institution = data[3]
        program_institution.pgm_id = program_institution.pgm_id.astype(str)
        program_institution.ins_id = program_institution.ins_id.astype(str)

        institution_info = data[4]

        programs, addresses, program_personnel, program_institution, institution_info = self._select_values(
            programs, addresses, program_personnel, program_institution, institution_info
        )
        program_information, institution_info, program_personnel = self._merge_dataframes(programs,
                                                                                          addresses,
                                                                                          institution_info,
                                                                                          program_institution,
                                                                                          program_personnel
                                                                                          )
        program_personnel = self._generate_primary_keys(program_personnel)

        return [program_information, program_personnel, institution_info]

    @classmethod
    def _select_values(cls, programs, addresses, program_personnel, program_institution, institution_info):
        programs = programs.loc[(programs['pgm_activity_code'] == '0')].reset_index(drop=True)

        addresses = addresses.loc[(addresses['addr_type'] == 'D')].reset_index(drop=True)

        program_personnel_member = program_personnel.loc[(program_personnel['pers_type'] == 'D')]

        program_institution = program_institution.loc[
            (program_institution['affiliation_type'] == 'S')
        ].reset_index(drop=True)

        institution_info = institution_info.loc[
            (institution_info['ins_affiliation_type'] == 'S')
        ].reset_index(drop=True)

        return programs, addresses, program_personnel_member, program_institution, institution_info

    @classmethod
    def _merge_dataframes(cls, programs, addresses, institution_info, program_institution, program_personnel):
        import pdb
        pdb.set_trace()
        program_information = programs.merge(addresses, on='pgm_id', how='left')
        program_information = program_information.merge(program_institution[
                                                            ['pgm_id', 'ins_id', 'pri_clinical_loc_ind']
                                                        ], on='pgm_id', how='left')

        institution_info = institution_info.merge(program_institution[['ins_id']], on='ins_id', how='left')
        institution_info['last_upd_dt'] = institution_info['last_upd_dt'].fillna(
            value=pandas.to_datetime('01/01/1970'))

        program_personnel['last_upd_dt'] = program_personnel['last_upd_dt'].fillna(
            value=pandas.to_datetime('01/01/1970'))

        return program_information, institution_info, program_personnel

    @classmethod
    def _generate_primary_keys(cls, dataframe):
        primary_keys = dask.array.array([str(column['pgm_id']) + str(column['aamc_id'])
                                         for index, column in dataframe.iterrows()])
        dataframe['id'] = primary_keys

        return dataframe

    def _get_columns(self):
        return [PROGRAM_COLUMNS, MEMBER_COLUMNS, INSTITUTION_COLUMNS]
