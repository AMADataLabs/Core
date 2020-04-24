"""
Preferred office location (POLO) address fitness model class.

TODO: remove code elsewhere that uses the function score_polo_addr_ppd_data.score_polo_wslive_data()
"""
from   collections import namedtuple
from   dataclasses import dataclass
import datetime
import logging
import os
from   pathlib import Path
from   typing import Iterable, Set

import pandas as pd

from   class_model_creation import get_class_predictions
from   create_addr_model_input_data import create_ppd_scoring_data
from   process_model_data import convert_data_types, create_new_addr_vars, clean_model_data, convert_int_to_cat

from   datalabs.analysis.exception import InvalidDataException
import datalabs.curate.dataframe  # pylint: disable=unused-import

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


ModelVariables = namedtuple('ModelVariables', 'input output')
@dataclass
class ModelVariables:
    input: Set
    feature: Iterable
    output: Set


@dataclass
class EntityData:
    entity_comm_at: 'str or DataFrame'
    entity_comm_usg: 'str or DataFrame'
    post_addr_at: 'str or DataFrame'
    license_lt: 'str or DataFrame'
    entity_key_et: 'str or DataFrame'


@dataclass
class ModelInputData:
    model: 'str or XGBClassifier'
    variables: ModelVariables
    ppd: 'str or DataFrame'
    entity: EntityData
    date: datetime.datetime


@dataclass
class ModelPredictions:
    pclass: Iterable
    probability: Iterable


class POLOFitnessModel():
    '''POLO address fitness model'''

    def __init__(self, archive_dir):
        self._archive_dir = archive_dir
        self._start_time = None
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
        self._start_time = datetime.datetime.now()

        merged_input_data = self._merge_ppd_and_aims_data(input_data.ppd, input_data.entity)

        model_input_data, cleaned_merged_data = self._curate_input_data_for_model(merged_input_data, input_data.variables)

        self._archive_model_input_data(model_input_data)

        scored_data =  self._score(input_data.model, input_data.variables, model_input_data, cleaned_merged_data)

        return scored_data

    def _merge_ppd_and_aims_data(self, ppd_data, entity_data):
        LOGGER.info('-- Merging PPD and AIMS Data --')

        start_time = datetime.datetime.now()
        merged_input_data = create_ppd_scoring_data(
            ppd_data, self.ppd_date,
            entity_data.entity_comm_at, entity_data.entity_comm_usg,
            entity_data.post_addr_at, entity_data.license_lt, entity_data.entity_key_et)
        LOGGER.debug('Merge duration: %d s', (datetime.datetime.now()-start_time).seconds)
        LOGGER.debug('Model input data length: %s', len(merged_input_data))

        start_time = datetime.datetime.now()
        self._archive_merged_input_data(merged_input_data)
        LOGGER.debug('Archive duration: %d s', (datetime.datetime.now()-start_time).seconds)

        start_time = datetime.datetime.now()
        converted_input_data = convert_data_types(merged_input_data)
        LOGGER.debug('Conversion duration: %d s', (datetime.datetime.now()-start_time).seconds)

        return converted_input_data

    def _curate_input_data_for_model(self, merged_input_data, variables):
        LOGGER.info('-- Creating Scoring Model Input Data --')

        model_input_data, cleaned_merged_data = self._generate_features(merged_input_data, variables)

        pruned_model_input_data = self._prune_and_patch_model_input_data(model_input_data, variables)

        return pruned_model_input_data, cleaned_merged_data

    def _archive_model_input_data(self, model_input_data):
        LOGGER.info('-- Archiving Model Input Data --')

        model_input_filename = '{}_PPD_{}_Polo_Addr_Rank_Input_Data.csv'.format(
            self.start_datestamp, self.ppd_datestamp
        )
        model_input_path = Path(self._archive_dir, model_input_filename)

        LOGGER.info('Archiving pruned model input data to %s', model_input_path)
        model_input_data.to_csv(model_input_path, sep=',', header=True, index=True)

    @classmethod
    def _score(cls, model, variables, model_input_data, merged_input_data):
        LOGGER.info('-- Predicting Fitness of POLO Addresses --')

        predictions = cls._predict(model, model_input_data)

        scored_data = cls._generate_scored_data(merged_input_data, variables, predictions)

        return scored_data

    def _archive_merged_input_data(self, merged_input_data):
        ppd_entity_filename = '{}_PPD_{}_Polo_Addr_Rank_PPD_Entity_Data.csv'.format(
            self.start_datestamp, self.ppd_datestamp
        )
        ppd_entity_path = Path(self._archive_dir, ppd_entity_filename)

        LOGGER.info('Archiving scoring data to %s', ppd_entity_path)
        merged_input_data.to_csv(ppd_entity_path, sep=',', header=True, index=True)

    @classmethod
    def _generate_features(cls, merged_input_data, variables):
        initial_feature_data = create_new_addr_vars(merged_input_data)

        # Get data with just model variables
        model_data = initial_feature_data.loc[:, variables.input]

        cls._assert_has_columns(variables.input, model_data)

        # Deal with any NaN or invalid entries
        cleaned_model_data, cleaned_merged_data = clean_model_data(model_data, merged_input_data)

        # Convert int variables to integer from float
        converted_model_data = convert_int_to_cat(cleaned_model_data)

        # Convert categorical variables to dummy variables
        model_feature_data = pd.get_dummies(converted_model_data)

        cls._assert_has_columns(variables.feature, model_feature_data)

        return model_feature_data, cleaned_merged_data

    @classmethod
    def _prune_and_patch_model_input_data(cls, model_input_data, variables):
        pruned_model_input_data = model_input_data.loc[:, variables.feature]

        return cls._fill_nan(pruned_model_input_data)

    @classmethod
    def _predict(cls, metaparameters, model_input_data):
        LOGGER.info('-- Applying POLO model --')
        predictions = get_class_predictions(metaparameters, model_input_data, 0.5, False)

        return ModelPredictions(pclass=predictions[0], probability=predictions[1])

    @classmethod
    def _generate_scored_data(cls, merged_input_data, variables, predictions):
        scored_data = merged_input_data.loc[:, variables.output]

        scored_data = cls._add_fitness_scores(scored_data, predictions)

        return scored_data.datalabs.rename_in_upper_case()

    @classmethod
    def _assert_has_columns(cls, column_names, data):
        LOGGER.debug('Expected the following columns: %s', column_names)
        LOGGER.debug('DataFrame columns: %s', data.columns.values)
        missing_columns = [c for c in column_names if c not in data.columns.values]
        if missing_columns:
            raise InvalidDataException(f'The data is missing the following columns: {missing_columns}')

    @classmethod
    def _fill_nan(cls, data):
        for name in data.columns.values:
            if all(data[name].isna()):
                data[name] = 0

        return data

    @classmethod
    def _add_fitness_scores(cls, scored_data, predictions):
        scored_data['pred_class'] = predictions.pclass
        scored_data['pred_probability'] = predictions.probability

        return scored_data


