"""
Preferred office location (POLO) address fitness model class.

TODO: remove code elsewhere that uses the function score_polo_addr_ppd_data.score_polo_wslive_data()
"""
from   collections import namedtuple
import datetime
import logging
import os
from   pathlib import Path

import pandas as pd

import settings
from   score_polo_addr_ppd_data import score_polo_ppd_data
from   class_model_creation import get_class_predictions
from   create_addr_model_input_data import create_ppd_scoring_data
from   process_model_data import convert_data_types, create_new_addr_vars, clean_model_data, convert_int_to_cat

from   datalabs.analysis.exception import InvalidDataException
import datalabs.curate.dataframe  # pylint: disable=unused-import

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


ModelInputData = namedtuple('ModelInputData', 'model ppd entity date')
EntityData = namedtuple('EntityData', 'entity_comm_at entity_comm_usg post_addr_at license_lt entity_key_et')
ModelParameters = namedtuple('ModelParameters', 'meta variables')


class POLOFitnessModel():
    '''POLO address fitness model'''

    def __init__(self, archive_dir):
        self._archive_dir = archive_dir
        self._start_time = datetime.datetime.now()
        self._ppd_datestamp = None

        if not os.path.exists(self._archive_dir):
            os.mkdir(self._archive_dir)

    @property
    def start_time(self):
        return self._start_time

    @property
    def start_datestamp(self):
        return self._start_time.strftime("%Y-%m-%d")

    @property
    def ppd_datestamp(self):
        return self._ppd_datestamp

    @property
    def ppd_date(self):
        return datetime.datetime.strptime(self._ppd_datestamp, '%Y%m%d')

    def apply(self, input_data: ModelInputData) -> pd.DataFrame:
        '''Apply the POLO address fitness model to AIMS data.'''
        self._ppd_datestamp = input_data.date

        scored_data, pruned_model_input_data = self._score(input_data)

        self._archive_pruned_model_input_data(pruned_model_input_data)

        return scored_data

    def _score(self, input_data):
        self._start_time = datetime.datetime.now()
        merged_input_data = self._merge_input_data(input_data)

        LOGGER.info('-- Applying POLO model --')

        # note these are in the order desired for the sample output
        info_vars = ['ppd_me', 'ppd_first_name', 'ppd_middle_name', 'ppd_last_name', 'ppd_suffix',
                     'ppd_polo_mailing_line_1', 'ppd_polo_mailing_line_2', 'ppd_polo_city',
                     'ppd_polo_state', 'ppd_polo_zip',
                     'ppd_telephone_number', 'ppd_prim_spec_cd', 'ppd_pe_cd', 'ppd_fax_number',
                     'post_addr_line1', 'post_addr_line2', 'post_city_cd', 'post_state_cd',
                     'post_zip', 'ent_comm_comm_type', 'ent_comm_begin_dt', 'ent_comm_end_dt',
                     'ent_comm_comm_id', 'ent_comm_entity_id']

        LOGGER.debug('SCORE_POLO_ADDR_DATA')
        LOGGER.debug(ppd_scoring_df.dtypes)

        # Convert data types to expected
        assert 'ent_comm_begin_dt' in ppd_scoring_df.columns.values
        MISSING_VARIABLES = [
            'lic_state_match_0', 'ent_comm_src_cat_code_ADMIT-HOS', 'ent_comm_src_cat_code_ECF-CNVRSN',
            'ent_comm_src_cat_code_GROUP', 'ent_comm_src_cat_code_PHNSURV', 'ent_comm_src_cat_code_SCHL-HOSP',
            'ent_comm_comm_type_GROUP', 'ppd_pe_cd_11', 'ppd_pe_cd_110',
        ]

        ppd_scoring_converted_df = convert_data_types(ppd_scoring_df)

        # Create new model variables
        ppd_scoring_new_df = create_new_addr_vars(ppd_scoring_converted_df)

        # Get data with just model variables
        model_df = self._filter_out_extra_variables(ppd_scoring_new_df)

        # Deal with any NaN or invalid entries
        model_clean_df = clean_model_data(model_df, ppd_scoring_new_df)

        # Convert int variables to integer from float
        model_convert_df = convert_int_to_cat(model_clean_df)

        # Convert categorical variables to dummy variables
        model_data_all = pd.get_dummies(model_convert_df)

        # Keep only variable required for the model
        model_vars = list(model_vars)

        missing_variables = [var for var in model_vars if var not in model_data_all.columns.values]
        if missing_variables:
            raise InvalidDataException(f'Model input data is missing the following columns: {missing_variables}')

        pruned_model_input_data = model_data_all.loc[:, input_data.model.variables]
        pruned_model_input_data = fill_nan_model_vars(pruned_model_input_data)

        # get model class probabilites and predictions
        preds, probs = get_class_predictions(input_data.model.meta, pruned_model_input_data, 0.5, False)

        scored_data = model_df[:]
        scored_data[info_vars] = scored_data.loc[:, info_vars]
        scored_data['pred_class'] = preds
        scored_data['pred_probability'] = probs

        LOGGER.debug('Scored data length: %s', len(scored_data))

        scored_data = scored_data.datalabs.rename_in_upper_case()

        return scored_data, pruned_model_input_data

    def _merge_input_data(self, input_data):
        LOGGER.info('-- Creating Scoring Model Input Data --')

        merged_input_data = create_ppd_scoring_data(
            input_data.ppd, self.ppd_date,
            input_data.entity.entity_comm_at, input_data.entity.entity_comm_usg,
            input_data.entity.post_addr_at, input_data.entity.license_lt, input_data.entity.entity_key_et)
        LOGGER.debug('Model input data length: %s', len(merged_input_data))

        assert 'ent_comm_begin_dt' in merged_input_data.columns.values

        self._archive_merged_input_data(merged_input_data)

        return merged_input_data

    def _archive_merged_input_data(self, merged_input_data):
        ppd_entity_filename = '{}_PPD_{}_Polo_Addr_Rank_PPD_Entity_Data.csv'.format(
            self.start_datestamp, self.ppd_datestamp
        )
        ppd_entity_path = Path(self._archive_dir, ppd_entity_filename)

        LOGGER.info('Archiving scoring data to %s', ppd_entity_path)
        merged_input_data.to_csv(ppd_entity_path, sep=',', header=True, index=True)

    def _archive_pruned_model_input_data(self, pruned_model_input_data):
        model_input_filename = '{}_PPD_{}_Polo_Addr_Rank_Input_Data.csv'.format(
            self.start_datestamp, self.ppd_datestamp
        )
        model_input_path = Path(self._archive_dir, model_input_filename)

        LOGGER.info('Archiving pruned model input data to %s', model_input_path)
        pruned_model_input_data.to_csv(model_input_path, sep=',', header=True, index=True)

    @classmethod
    def _filter_out_extra_variables(cls, data):
        required_input_data_variables = [
            'addr_age_yrs',
            'curr_ent_all_addr_count',
            'curr_ent_id_addr_count',
            'curr_usg_all_addr_count',
            'doctor_age_yrs',
            'ent_comm_comm_type',
            'ent_comm_src_cat_code',
            'hist_ent_all_addr_count',
            'hist_ent_id_addr_count',
            'lic_state_match',
            'pcp',
            'ppd_address_type',
            'ppd_division',
            'ppd_gender',
            'ppd_group',
            'ppd_md_do_code',
            'ppd_micro_metro_ind',
            'ppd_msa_population_size',
            'ppd_pe_cd',
            'ppd_polo_state',
            'ppd_prim_spec_cd',
            'ppd_region',
            'ppd_top_cd',
            'yop_yrs'
        ]

        return data.loc[:, required_input_data_variables]



def fill_nan_model_vars(data_df):
    data_cols = data_df.columns.values
    for name in data_cols:

        if all(data_df[name].isna()):
            data_df[name] = 0

    return data_df


