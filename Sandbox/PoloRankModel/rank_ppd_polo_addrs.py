'''
Run the POLO address rank scoring model using PPD and AIMS data.

Kari Palmier    7/31/19    Created
Kari Palmier    8/14/19    Updated to work with more generic get_sample
'''
from   collections import namedtuple
import datetime
import logging
import os
import pickle
import re
import sys
import warnings

import dotenv
import pandas as pd

dotenv.load_dotenv()
map(lambda p: sys.path.insert(0, p), os.environ.get('DATALABS_PYTHONPATH', '').split(':')[::-1])

# from get_ppd import get_latest_ppd_data
from capitalize_column_names import capitalize_column_names  # pylint: disable=wrong-import-position
from score_polo_addr_ppd_data import score_polo_ppd_data  # pylint: disable=wrong-import-position
from class_model_creation import get_prob_info, get_pred_info  # pylint: disable=wrong-import-position
from create_addr_model_input_data import create_ppd_scoring_data  # pylint: disable=wrong-import-position

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

warnings.filterwarnings("ignore")


InputData = namedtuple('InputData', 'ppd entity')
EntityData = namedtuple('EntityData', 'entity_comm_at entity_comm_usg post_addr_at license_lt entity_key_et')
ModelData = namedtuple('ModelData', 'model variables')


class InvalidDataException(Exception):
    pass


class PoloRankModel():
    def __init__(self):
        self._start_time = datetime.datetime.now()
        self._ppd_score_out_dir = os.environ.get('PPD_SCORE_OUT_DIR')
        self._ppd_archive_dir = self._ppd_score_out_dir + '_Archived'
        self._model_file = os.environ.get('MODEL_FILE')
        self._model_var_file = os.environ.get('MODEL_VAR_FILE')
        self._model_predictions_path = os.environ.get('MODEL_PREDICTIONS_FILE')
        self._ppd_datestamp = None


        if not os.path.exists(self._ppd_archive_dir):
            os.mkdir(self._ppd_archive_dir)

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

        self._score_predictions(model_predictions)


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
            model=pickle.load(open(self._model_file, 'rb')),
            variables=pickle.load(open(self._model_var_file, 'rb'))
        )


    def _generate_model_input_data(self, input_data):
        LOGGER.info('-- Creating Scoring Model Input Data --')

        model_input_data = create_ppd_scoring_data(
            input_data.ppd, input_data.date,
            input_data.entity.ent_comm_at, input_data.entity.ent_comm_usg,
            input_data.entity.post_addr_at, input_data.entity.license_lt, input_data.entity.ent_key_et)
        LOGGER.debug(f'Model input data length: {len(model_input_data)}')

        assert 'ent_comm_begin_dt' in model_input_data.columns.values

        self._archive_model_input_data(model_input_data, input_data.date)

        return model_input_data

    def _run_model(self, parameters, input_data):
        LOGGER.info('-- Applying scoring model --')
        model_predictions, pruned_model_input_data = score_polo_ppd_data(
            input_data, parameters.model, parameters.variables
        )
        LOGGER.debug(f'Model predictions length: {len(model_predictions)}')

        model_predictions = capitalize_column_names(model_predictions)

        self._save_model_predictions(model_predictions)

        self._archive_pruned_model_input_data(pruned_model_input_data)

        return model_predictions

    def _score_model_predictions(self, model_predictions):
        model_predictions['RANK_ROUND'] = model_predictions['PRED_PROBABILITY'].apply(lambda x: round((x * 10)))
        zero_ndx = model_predictions['RANK_ROUND'] == 0
        model_predictions.loc[zero_ndx, 'RANK_ROUND'] = 1

        LOGGER.debug('Length of model_predictions: {}'.format(len(model_predictions)))

        get_prob_info(model_predictions['PRED_PROBABILITY'])
        get_pred_info(model_predictions['PRED_CLASS'])

        self._save_scored_model_predictions(scored_model_predictions)

        self._archive_model_predictions(scored_model_predictions)

        return model_predictions

    def _get_ppd_data(self):
        ppd_file = os.environ.get('PPD_FILE')
        require_latest_ppd_data = True if os.environ.get('REQUIRE_LATEST_PPD_DATA').lower() == 'true' else False
        ppd_data = None

        LOGGER.info('--- Loading PPD Data ---')

        if require_latest_ppd_data:
            ppd_data, ppd_datestamp = get_latest_ppd_data_and_datestamp()
        else:
            ppd_data, ppd_datestamp = self._extract_ppd_data_and_datestamp_from_file(ppd_file)

        self._ppd_datestamp

        return ppd_data

    def _get_entity_data(self):
        LOGGER.info('--- Loading Entity Data ---')

        return EntityData(
            entity_comm_at=extract_entity_data_from_file(os.environ.get('ENTITY_COMM_AT_FILE')),
            entity_comm_usg=extract_entity_data_from_file(os.environ.get('ENTITY_COMM_USG_FILE')),
            post_addr_at=extract_entity_data_from_file(os.environ.get('POST_ADDR_AT_FILE')),
            license_lt=extract_entity_data_from_file(os.environ.get('LICENSE_LT_FILE')),
            entity_key_et=extract_entity_data_from_file(os.environ.get('ENTITY_KEY_ET_FILE')),
        )

    def _archive_model_input_data(self, model_input_data):
        ppd_entity_filename = '{}_PPD_{}_Polo_Addr_Rank_PPD_Entity_Data.csv'.format(
            self.start_datestamp, self.ppd_datestamp
        )
        ppd_entity_path = Path(self._ppd_archive_dir, ppd_entity_filename)

        LOGGER.info('-- Archiving scoring data to {} --'.format(ppd_entity_path))
        model_input_data.to_csv(ppd_entity_file, sep=',', header=True, index=True)

    def _save_model_predictions(self, model_predictions):
        LOGGER.info(f'-- Writing Model Predictions to {self._model_predictions_path} --')
        model_predictions.to_csv(self._model_predictions_path, index=False)

    def _archive_pruned_model_input_data(self, pruned_model_input_data):
        model_input_filename = '{}_PPD_{}_Polo_Addr_Rank_Input_Data.csv'.format(
            self.start_timestamp, self.ppd_datestamp
        )
        model_input_path = Path(self._ppd_archive_dir, model_input_filename)

        LOGGER.info('-- Archiving pruned model input data to {} --'.format(ppd_entity_path))
        pruned_model_input_data.to_csv(model_input_path, sep=',', header=True, index=True)

    def _save_scored_model_predictions(self, scored_model_predictions):
        scored_predictions_path = self._ppd_score_out_dir + 'Polo_Addr_Rank_Scored_PPD_DPC_Pop.csv'
        print('\tsaving predictions to {}'.format(ppd_score_out_dir))
        scored_model_predictions.to_csv(scored_predictions_path, sep=',', header=True, index=True)

    def _archive_scored_model_predictions(self, scored_model_predictions):
        scored_predictions_filename =  '{}_PPD_{}_Polo_Addr_Rank_Scored_PPD_DPC_Pop.csv'.format(
            self.start_timestamp, ppd_date_str
        )
        scored_predictions_path = Path(self._ppd_archive_dir, scored_predictions_filename)

        scored_model_predictions.to_csv(scored_predictions_path, sep=',', header=True, index=True)


    def _get_latest_ppd_data_and_datestamp(self):
        ppd_data, ppd_datestamp = get_latest_ppd_data()

        return ppd_data, ppd_datestamp

    def _extract_ppd_data_and_datestamp_from_file(self, ppd_file):
        ppd_data = pd.read_csv(ppd_file, dtype=str)

        ppd_datestamp = extract_ppd_date_from_filename(ppd_file)

        return ppd_data, ppd_datestamp

    def _extract_entity_data_from_file(self, filename):
        return pd.read_csv(filename, dtype=str, na_values=['', '(null)'])

    def _extract_ppd_date_from_filename(self, ppd_file):
        """ Extract the timestamp from a PPD data file path of the form '.../ppd_data_YYYYMMDD.csv'. """
        ppd_filename = Path(ppd_file).name

        match = re.match(r'ppd_data_([0-9]+)\.csv', path.name)

        return match.group(1)


    def _convert_timestamp_to_datetime(self, ppd_timestamp):
        return datetime.datetime.strptime(ppd_timestamp, '%Y%m%d')


if __name__ == '__main__':
    PoloRankModel().run()
