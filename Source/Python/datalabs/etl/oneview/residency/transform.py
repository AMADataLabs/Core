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
    def _csv_to_dataframe(cls, data, on_disk, **kwargs):
        return super()._csv_to_dataframe(data, on_disk, sep='|', error_bad_lines=False, encoding='latin',
                                         low_memory=False)

    # pylint: disable=too-many-arguments
    def _preprocess_data(self, data):
        programs, addresses, program_personnel, program_institution, institution_info = data

        addresses, program_personnel, program_institution = self._convert_ids_to_strings(
            addresses,
            program_personnel,
            program_institution
        )

        programs, addresses, program_personnel, program_institution, institution_info = self._select_values(
            programs,
            addresses,
            program_personnel,
            program_institution,
            institution_info
        )

        programs, program_personnel, institution_info = self._merge_dataframes(
            programs,
            addresses,
            program_personnel,
            program_institution,
            institution_info
        )

        programs, program_personnel, institution_info = self._set_defaults(
            programs,
            program_personnel,
            institution_info
        )

        programs = self._convert_integers_to_booleans(programs)

        program_personnel = self._generate_primary_keys(program_personnel)

        return [programs, program_personnel, institution_info]

    @classmethod
    def _convert_ids_to_strings(cls, addresses, program_personnel, program_institution):
        addresses.pgm_id = addresses.pgm_id.astype(str)

        program_personnel.pgm_id = program_personnel.pgm_id.astype(str)

        program_institution = program_institution.astype({'pgm_id': str, 'ins_id': str})

        return addresses, program_personnel, program_institution

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
    def _merge_dataframes(cls, programs, addresses, program_personnel, program_institution, institution_info):
        programs = programs.merge(addresses, on='pgm_id', how='left')
        programs = programs.merge(
            program_institution[['pgm_id', 'ins_id', 'pri_clinical_loc_ind']],
            on='pgm_id',
            how='left'
        )

        institution_info = institution_info.merge(
            program_institution[['ins_id']],
            on='ins_id',
            how='left'
        ).drop_duplicates()

        return programs, program_personnel, institution_info

    @classmethod
    def _set_defaults(cls, programs, program_personnel, institution_info):
        programs['pgm_chg_size'] = programs['pgm_chg_size'].fillna(value=0)
        # programs['pgm_oth_match'] = programs['pgm_oth_match'].fillna(value='')
        programs = programs.fillna({column:0 for column in col.PROGRAM_BOOLEAN_COLUMNS})
        programs['pgm_init_accred_dt'] = programs['pgm_init_accred_dt'].fillna(
            value=pandas.to_datetime('01/01/1970')
        )
        programs = programs.fillna('')
        import pdb; pdb.set_trace()

        program_personnel['last_upd_dt'] = program_personnel['last_upd_dt'].fillna(
            value=pandas.to_datetime('01/01/1970')
        )

        institution_info['last_upd_dt'] = institution_info['last_upd_dt'].fillna(
            value=pandas.to_datetime('01/01/1970')
        )

        return programs, program_personnel, institution_info

    @classmethod
    def _convert_integers_to_booleans(cls, programs):
        programs = programs.astype({column:'int' for column in col.PROGRAM_BOOLEAN_COLUMNS})
        programs = programs.astype({column:'boolean' for column in col.PROGRAM_BOOLEAN_COLUMNS})

        return programs

    @classmethod
    def _generate_primary_keys(cls, program_personnel):
        program_personnel['id'] = program_personnel['pgm_id'].astype(str) + program_personnel['aamc_id'].astype(str)

        return program_personnel

    def _get_columns(self):
        return [col.PROGRAM_COLUMNS, col.MEMBER_COLUMNS, col.INSTITUTION_COLUMNS]
