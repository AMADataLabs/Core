'''
Run the POLO address rank scoring model using PPD and AIMS data.

Kari Palmier    7/31/19    Created
Kari Palmier    8/14/19    Updated to work with more generic get_sample
'''
from   collections import namedtuple
import datetime
import logging
import os
from   pathlib import Path
import pickle
import re
import sys
import warnings

import pandas as pd

import settings
from capitalize_column_names import capitalize_column_names
from score_polo_addr_ppd_data import score_polo_ppd_data  # pylint: disable=wrong-import-position
from class_model_creation import get_prob_info, get_pred_info  # pylint: disable=wrong-import-position
from create_addr_model_input_data import create_ppd_scoring_data  # pylint: disable=wrong-import-position

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

warnings.filterwarnings("ignore")


InputData = namedtuple('InputData', 'ppd entity')
EntityData = namedtuple('EntityData', 'entity_comm_at entity_comm_usg post_addr_at license_lt entity_key_et')
ModelData = namedtuple('ModelData', 'model variables predictions scored_predictions')


class InvalidDataException(Exception):
    pass


class PoloRankModel():
    def __init__(self):
        entity_files = EntityData(
            entity_comm_at=os.environ.get('ENTITY_COMM_AT_FILE'),
            entity_comm_usg=os.environ.get('ENTITY_COMM_USG_FILE'),
            post_addr_at=os.environ.get('POST_ADDR_AT_FILE'),
            license_lt=os.environ.get('LICENSE_LT_FILE'),
            entity_key_et=os.environ.get('ENTITY_KEY_ET_FILE')
        )

        self._input_files = InputData(
            ppd=os.environ.get('PPD_FILE'),
            entity=entity_files
        )
        self._model_files = ModelData(
            model=os.environ.get('MODEL_FILE'),
            variables=os.environ.get('MODEL_VAR_FILE'),
            predictions=os.environ.get('MODEL_PREDICTIONS_FILE'),
            scored_predictions=os.environ.get('MODEL_SCORED_PREDICTIONS_FILE')
        )
        self._archive_dir = os.environ.get('MODEL_ARCHIVE_DIR')
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

    def run(self):
        self._start_time = datetime.datetime.now()

        input_data = self._get_input_data()

        model_parameters = self._get_model_parameters()

        model_input_data = self._generate_model_input_data(input_data)

        model_predictions = self._run_model(model_parameters, model_input_data)

        self._score_model_predictions(model_predictions)


    def _get_input_data(self):
        ppd_data = self._get_ppd_data()

        entity_data = self._get_entity_data()

        if len(entity_data.entity_comm_at) == 0:
            raise InvalidDataException('No ent_comm_at entity data was loaded.')

        if len(entity_data.entity_comm_usg) == 0:
            raise InvalidDataException('No ent_comm_usg entity data was loaded.')

        return InputData(ppd=ppd_data, entity=entity_data)


    def _get_model_parameters(self):
        LOGGER.info('-- Loading Model Parameters --')

        return ModelData(
            model=pickle.load(open(self._model_files.model, 'rb')),
            variables=pickle.load(open(self._model_files.variables, 'rb')),
            predictions=None,
            scored_predictions=None
        )


    def _generate_model_input_data(self, input_data):
        LOGGER.info('-- Creating Scoring Model Input Data --')

        model_input_data = create_ppd_scoring_data(
            input_data.ppd, pd.to_datetime('2020-02-22'),
            input_data.entity.entity_comm_at, input_data.entity.entity_comm_usg,
            input_data.entity.post_addr_at, input_data.entity.license_lt, input_data.entity.entity_key_et)
        LOGGER.debug('Model input data length: %s', len(model_input_data))

        assert 'ent_comm_begin_dt' in model_input_data.columns.values

        self._archive_model_input_data(model_input_data)

        return model_input_data

    def _run_model(self, parameters, input_data):
        LOGGER.info('-- Applying scoring model --')
        model_predictions, pruned_model_input_data = score_polo_ppd_data(
            input_data, parameters.model, parameters.variables
        )
        LOGGER.debug('Model predictions length: %s', len(model_predictions))

        model_predictions = capitalize_column_names(model_predictions)

        self._save_model_predictions(model_predictions)

        self._archive_pruned_model_input_data(pruned_model_input_data)

        return model_predictions

    def _score_model_predictions(self, model_predictions):
        model_predictions['RANK_ROUND'] = model_predictions['PRED_PROBABILITY'].apply(lambda x: round((x * 10)))
        zero_ndx = model_predictions['RANK_ROUND'] == 0
        model_predictions.loc[zero_ndx, 'RANK_ROUND'] = 1

        LOGGER.debug('Length of model_predictions: %s', len(model_predictions))

        get_prob_info(model_predictions['PRED_PROBABILITY'])
        get_pred_info(model_predictions['PRED_CLASS'])

        self._save_scored_model_predictions(model_predictions)

        self._archive_scored_model_predictions(model_predictions)

        return model_predictions

    def _get_ppd_data(self):
        LOGGER.info('--- Loading PPD Data ---')

        ppd_data = pd.read_csv(self._input_files.ppd, dtype=str)

        self._ppd_datestamp = self._extract_ppd_date_from_filename(self._input_files.ppd)

        return ppd_data

    def _get_entity_data(self):
        LOGGER.info('--- Loading Entity Data ---')

        return EntityData(
            entity_comm_at=self._extract_entity_data_from_file(self._input_files.entity.entity_comm_at),
            entity_comm_usg=self._extract_entity_data_from_file(self._input_files.entity.entity_comm_usg),
            post_addr_at=self._extract_entity_data_from_file(self._input_files.entity.post_addr_at),
            license_lt=self._extract_entity_data_from_file(self._input_files.entity.license_lt),
            entity_key_et=self._extract_entity_data_from_file(self._input_files.entity.entity_key_et),
        )

    def _archive_model_input_data(self, model_input_data):
        ppd_entity_filename = '{}_PPD_{}_Polo_Addr_Rank_PPD_Entity_Data.csv'.format(
            self.start_datestamp, self.ppd_datestamp
        )
        ppd_entity_path = Path(self._archive_dir, ppd_entity_filename)

        LOGGER.info('Archiving scoring data to %s', ppd_entity_path)
        model_input_data.to_csv(ppd_entity_path, sep=',', header=True, index=True)

    def _save_model_predictions(self, model_predictions):
        LOGGER.info('Writing model predictions to %s', self._model_files.predictions)
        model_predictions.to_csv(self._model_files.predictions, index=False)

    def _archive_pruned_model_input_data(self, pruned_model_input_data):
        model_input_filename = '{}_PPD_{}_Polo_Addr_Rank_Input_Data.csv'.format(
            self.start_datestamp, self.ppd_datestamp
        )
        model_input_path = Path(self._archive_dir, model_input_filename)

        LOGGER.info('Archiving pruned model input data to %s', model_input_path)
        pruned_model_input_data.to_csv(model_input_path, sep=',', header=True, index=True)

    def _save_scored_model_predictions(self, scored_model_predictions):
        LOGGER.info('Saving scored predictions to %s', self._model_files.scored_predictions)
        scored_model_predictions.to_csv(self._model_files.scored_predictions, sep=',', header=True, index=True)

    def _archive_scored_model_predictions(self, scored_model_predictions):
        scored_predictions_filename = '{}_PPD_{}_Polo_Addr_Rank_Scored_PPD_DPC_Pop.csv'.format(
            self.start_datestamp, self.ppd_datestamp
        )
        scored_predictions_path = Path(self._archive_dir, scored_predictions_filename)

        scored_model_predictions.to_csv(scored_predictions_path, sep=',', header=True, index=True)

    @classmethod
    def _extract_entity_data_from_file(cls, filename):
        return pd.read_csv(filename, dtype=str, na_values=['', '(null)'])

    @classmethod
    def _extract_ppd_date_from_filename(cls, ppd_file):
        """ Extract the timestamp from a PPD data file path of the form '.../ppd_data_YYYYMMDD.csv'. """
        ppd_filename = Path(ppd_file).name

        match = re.match(r'ppd_data_([0-9]+)\.csv', ppd_filename)

        return match.group(1)


    @classmethod
    def _convert_timestamp_to_datetime(cls, ppd_timestamp):
        return datetime.datetime.strptime(ppd_timestamp, '%Y%m%d')


if __name__ == '__main__':
    PoloRankModel().run()
