from   collections import namedtuple
import datetime
import logging
import os
from   pathlib import Path

import pandas as pd

import settings
from   score_polo_addr_ppd_data import score_polo_ppd_data  # pylint: disable=wrong-import-position
from   create_addr_model_input_data import create_ppd_scoring_data  # pylint: disable=wrong-import-position

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

    def apply(self, input_data: ModelInputData) -> ModelOutputData:
        '''Apply the POLO address fitness model to AIMS data.'''
        self._ppd_datestamp = input_data.date

        scored_data = self._score(input_data)

        self._plot(scored_data)

        return scored_data

    def _score(self, input_data):
        self._start_time = datetime.datetime.now()
        curated_input_data = self._curate_input_data(input_data)

        LOGGER.info('-- Applying POLO model --')
        scored_data, pruned_model_input_data = score_polo_ppd_data(
            curated_input_data, input_data.model.meta, input_data.model.variables
        )
        LOGGER.debug('Scored data length: %s', len(scored_data))

        scored_data = scored_data.datalabs.rename_in_upper_case()

        self._archive_pruned_model_input_data(pruned_model_input_data)

        return scored_data

    def _curate_input_data(self, input_data):
        LOGGER.info('-- Creating Scoring Model Input Data --')

        curated_input_data = create_ppd_scoring_data(
            input_data.ppd, self.ppd_date,
            input_data.entity.entity_comm_at, input_data.entity.entity_comm_usg,
            input_data.entity.post_addr_at, input_data.entity.license_lt, input_data.entity.entity_key_et)
        LOGGER.debug('Model input data length: %s', len(curated_input_data))

        assert 'ent_comm_begin_dt' in curated_input_data.columns.values

        self._archive_curated_input_data(curated_input_data)

        return curated_input_data

    def _archive_curated_input_data(self, curated_input_data):
        ppd_entity_filename = '{}_PPD_{}_Polo_Addr_Rank_PPD_Entity_Data.csv'.format(
            self.start_datestamp, self.ppd_datestamp
        )
        ppd_entity_path = Path(self._archive_dir, ppd_entity_filename)

        LOGGER.info('Archiving scoring data to %s', ppd_entity_path)
        curated_input_data.to_csv(ppd_entity_path, sep=',', header=True, index=True)

    def _archive_pruned_model_input_data(self, pruned_model_input_data):
        model_input_filename = '{}_PPD_{}_Polo_Addr_Rank_Input_Data.csv'.format(
            self.start_datestamp, self.ppd_datestamp
        )
        model_input_path = Path(self._archive_dir, model_input_filename)

        LOGGER.info('Archiving pruned model input data to %s', model_input_path)
        pruned_model_input_data.to_csv(model_input_path, sep=',', header=True, index=True)
