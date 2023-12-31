""" Oneview Residency Transformer"""
import logging
import pandas

import datalabs.etl.oneview.residency.column as col
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ResidencyTransformerTask(TransformerTask):
    @classmethod
    def _csv_to_dataframe(cls, data, **kwargs):
        return super()._csv_to_dataframe(data, sep='|', error_bad_lines=False, encoding='latin', low_memory=False)

    def _preprocess(self, dataset):
        programs, addresses, program_personnel, program_institutions, institution_info = dataset

        addresses, program_personnel, program_institutions = self._convert_ids_to_strings(
            addresses,
            program_personnel,
            program_institutions
        )

        programs, addresses, program_personnel, program_institutions, institution_info = self._select_values(
            programs,
            addresses,
            program_personnel,
            program_institutions,
            institution_info
        )

        programs, program_personnel, institution_info = self._merge(
            programs,
            addresses,
            program_personnel,
            program_institutions,
            institution_info
        )

        programs, program_personnel, institution_info = self._set_defaults(
            programs,
            program_personnel,
            institution_info
        )

        programs = self._convert_integers_to_booleans(programs)

        programs, program_personnel = self._filter_out_values(programs, institution_info, program_personnel)

        program_personnel = self._generate_primary_keys(program_personnel)

        return [programs, program_personnel, institution_info]

    @classmethod
    def _convert_ids_to_strings(cls, addresses, program_personnel, program_institutions):
        addresses.pgm_id = addresses.pgm_id.astype(str)

        program_personnel.pgm_id = program_personnel.pgm_id.astype(str)

        program_institutions = program_institutions.astype({'pgm_id': str, 'ins_id': str})

        return addresses, program_personnel, program_institutions

    # pylint: disable=too-many-arguments
    @classmethod
    def _select_values(cls, programs, addresses, program_personnel, program_institutions, institution_info):
        programs = programs.loc[(programs['pgm_activity_code'] == '0')].reset_index(drop=True)

        addresses = addresses.loc[(addresses['addr_type'] == 'D')].reset_index(drop=True)

        program_personnel_member = program_personnel.loc[(program_personnel['pers_type'] == 'D')]

        program_institutions = program_institutions.loc[
            (program_institutions['affiliation_type'] == 'S')
        ].reset_index(drop=True)

        institution_info = institution_info.loc[
            (institution_info['ins_affiliation_type'] == 'S')
        ].reset_index(drop=True)

        return programs, addresses, program_personnel_member, program_institutions, institution_info

    # pylint: disable=too-many-arguments
    @classmethod
    def _merge(cls, programs, addresses, program_personnel, program_institutions, institution_info):
        programs = programs.merge(addresses, on='pgm_id', how='left')
        programs = programs.merge(
            program_institutions[['pgm_id', 'ins_id', 'pri_clinical_loc_ind']],
            on='pgm_id',
            how='left'
        )

        institution_info = institution_info.merge(
            program_institutions[['ins_id']],
            on='ins_id',
            how='left'
        ).drop_duplicates()

        return programs, program_personnel, institution_info

    @classmethod
    def _set_defaults(cls, programs, program_personnel, institution_info):
        programs['pgm_chg_size'] = programs['pgm_chg_size'].fillna(value=0)
        programs = programs.fillna({column: 0 for column in col.PROGRAM_BOOLEAN_COLUMNS})
        programs['pgm_init_accred_dt'] = programs['pgm_init_accred_dt'].fillna(
            value=pandas.to_datetime('01/01/1970')
        )
        programs['pgm_accred_eff_dt'] = programs['pgm_accred_eff_dt'].fillna(
            value=pandas.to_datetime('01/01/1970')
        )
        program_personnel['last_upd_dt'] = program_personnel['last_upd_dt'].fillna(
            value=pandas.to_datetime('01/01/1970')
        )

        institution_info['last_upd_dt'] = institution_info['last_upd_dt'].fillna(
            value=pandas.to_datetime('01/01/1970')
        )

        programs['last_upd_dt_x'] = programs['last_upd_dt_x'].fillna(
            value=pandas.to_datetime('01/01/1970')
        )
        programs = programs.fillna('')

        return programs, program_personnel, institution_info

    @classmethod
    def _convert_integers_to_booleans(cls, programs):
        programs = programs.astype({column: 'int' for column in col.PROGRAM_BOOLEAN_COLUMNS})
        programs = programs.astype({column: 'boolean' for column in col.PROGRAM_BOOLEAN_COLUMNS})

        return programs

    @classmethod
    def _filter_out_values(cls, programs, institutions, program_personnel):
        unaccounted_values = list(set(programs.ins_id.to_list()) - set(institutions.ins_id.to_list()))
        programs = programs[~programs['ins_id'].isin(unaccounted_values)]

        unaccounted_values = list(set(program_personnel.pgm_id.to_list()) - set(programs.pgm_id.to_list()))
        program_personnel = program_personnel[~program_personnel['pgm_id'].isin(unaccounted_values)]

        return programs, program_personnel

    @classmethod
    def _generate_primary_keys(cls, program_personnel):
        program_personnel['id'] = program_personnel['pgm_id'].astype(str) + \
                                  program_personnel['pers_name_first'].astype(str) + \
                                  program_personnel['pers_name_mid'].astype(str) + \
                                  program_personnel['pers_name_last'].astype(str) + \
                                  program_personnel['pers_deg1'].astype(str)

        return program_personnel

    def _postprocess(self, dataset):
        programs, program_personnel, institution_info = dataset

        programs = programs[programs['institution'].notna()]

        return [programs, program_personnel, institution_info]

    def _get_columns(self):
        return [col.PROGRAM_COLUMNS, col.MEMBER_COLUMNS, col.INSTITUTION_COLUMNS]
