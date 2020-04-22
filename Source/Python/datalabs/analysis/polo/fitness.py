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
ModelVariables = namedtuple('ModelVariables', 'input feature output')


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

        merged_input_data = self._merge_ppd_and_aims_data(input_data)

        model_input_data = self._generate_features(merged_input_data, input_data.model.variables)

        pruned_model_input_data = self._prune_and_patch_model_input_data(model_input_data, input_data.model.variables)

        # get model class probabilites and predictions
        LOGGER.info('-- Applying POLO model --')
        preds, probs = get_class_predictions(input_data.model.meta, feature_data, 0.5, False)

        scored_data = output_feature_data.loc[:, input_data.model.variables.input]
        scored_data[input_data.model.variables.output] = merged_input_data.loc[:, input_data.model.variables.output]
        scored_data['pred_class'] = preds
        scored_data['pred_probability'] = probs

        LOGGER.debug('Scored data length: %s', len(scored_data))

        scored_data = scored_data.datalabs.rename_in_upper_case()

        return scored_data, feature_data

    def _archive_pruned_model_input_data(self, pruned_model_input_data):
        model_input_filename = '{}_PPD_{}_Polo_Addr_Rank_Input_Data.csv'.format(
            self.start_datestamp, self.ppd_datestamp
        )
        model_input_path = Path(self._archive_dir, model_input_filename)

        LOGGER.info('Archiving pruned model input data to %s', model_input_path)
        pruned_model_input_data.to_csv(model_input_path, sep=',', header=True, index=True)

    def _merge_ppd_and_aims_data(self, input_data):
        LOGGER.info('-- Creating Scoring Model Input Data --')

        merged_input_data = create_ppd_scoring_data(
            input_data.ppd, self.ppd_date,
            input_data.entity.entity_comm_at, input_data.entity.entity_comm_usg,
            input_data.entity.post_addr_at, input_data.entity.license_lt, input_data.entity.entity_key_et)
        LOGGER.debug('Model input data length: %s', len(merged_input_data))

        assert 'ent_comm_begin_dt' in merged_input_data.columns.values

        self._archive_merged_input_data(merged_input_data)


        return convert_data_types(merged_input_data)

    @classmethod
    def _generate_features(cls, merged_input_data, variables)
        initial_feature_data = create_new_addr_vars(merged_input_data)

        # Get data with just model variables
        model_data = initial_feature_data.loc[:, variables.input]

        cls._assert_has_columns(variables.input, model_data)

        # Deal with any NaN or invalid entries
        cleaned_model_data = clean_model_data(model_data, ppd_scoring_new_df)

        # Convert int variables to integer from float
        converted_model_data = convert_int_to_cat(cleaned_model_data)

        # Convert categorical variables to dummy variables
        model_feature_data = pd.get_dummies(converted_model_data)

        cls._assert_has_columns(variables.feature, model_feature_data)

        return model_feature_data

    def _prune_and_patch_model_input_data(cls, model_input_data, variables):
        pruned_model_input_data = model_input_data.loc[:, variables.feature]

        return fill_nan_model_vars(pruned_model_input_data)

    def _archive_merged_input_data(self, merged_input_data):
        ppd_entity_filename = '{}_PPD_{}_Polo_Addr_Rank_PPD_Entity_Data.csv'.format(
            self.start_datestamp, self.ppd_datestamp
        )
        ppd_entity_path = Path(self._archive_dir, ppd_entity_filename)

        LOGGER.info('Archiving scoring data to %s', ppd_entity_path)
        merged_input_data.to_csv(ppd_entity_path, sep=',', header=True, index=True)

    @classmethod
    def _assert_has_columns(cls, column_names, data):
        missing_columns = [c for c in column_names if c not in data.columns.values]
        if missing_columns:
            raise InvalidDataException(f'The data is missing the following columns: {missing_columns}')



def fill_nan_model_vars(data_df):
    data_cols = data_df.columns.values
    for name in data_cols:

        if all(data_df[name].isna()):
            data_df[name] = 0

    return data_df


