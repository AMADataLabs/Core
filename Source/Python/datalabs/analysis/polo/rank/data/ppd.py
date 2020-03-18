import logging
from   pathlib import Path
import pickle

import pandas as pd

from   datalabs.analysis.exception import InvalidDataException
from   datalabs.analysis.polo.rank.data.entity import EntityTableCleaner
from   datalabs.analysis.polo.rank.model import ModelInputData, ModelParameters, EntityData

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class InputDataLoader():
    def __init__(self, expected_df_lengths: ModelInputData=None):
        self._expected_df_lengths = expected_df_lengths

    def load(self, input_files: ModelInputData) -> ModelInputData:
        model_parameters = self._get_model_parameters(input_files.model)
        ppd_data = self._get_ppd_data(input_files.ppd)
        entity_data = self._get_entity_data(input_files.entity)

        return ModelInputData(model=model_parameters, ppd=ppd_data, entity=entity_data, date=input_files.date)

    @classmethod
    def _get_model_parameters(cls, model_files: ModelParameters) -> ModelParameters:
        LOGGER.info('-- Loading Model Parameters --')

        LOGGER.info('Reading Pickle file %s', model_files.meta)
        mata_parameters = pickle.load(open(model_files.meta, 'rb'))

        LOGGER.info('Reading Pickle file %s', model_files.variables)
        variables = pickle.load(open(model_files.variables, 'rb'))

        return ModelParameters(meta=mata_parameters, variables=variables)

    def _get_ppd_data(self, ppd_file: str) -> pd.DataFrame:
        LOGGER.info('--- Loading PPD Data ---')

        LOGGER.info('Reading CSV file %s', ppd_file)
        ppd_data = pd.read_csv(ppd_file, dtype=str)

        if self._expected_df_lengths:
            self._assert_reasonable_dataframe_length(self._expected_df_lengths.ppd, ppd_data)

        return ppd_data

    def _get_entity_data(self, entity_files: EntityData) -> EntityData:
        LOGGER.info('--- Loading Entity Data ---')

        return EntityData(
            entity_comm_at=self._extract_entity_data_from_file(entity_files, 'entity_comm_at'),
            entity_comm_usg=self._extract_entity_data_from_file(entity_files, 'entity_comm_usg'),
            post_addr_at=self._extract_entity_data_from_file(entity_files, 'post_addr_at'),
            license_lt=self._extract_entity_data_from_file(entity_files, 'license_lt'),
            entity_key_et=self._extract_entity_data_from_file(entity_files, 'entity_key_et'),
        )

    def _extract_entity_data_from_file(self, filenames, key):
        filename = getattr(filenames, key)
        extension = filename.rsplit('.')[-1]
        data = None

        if extension == 'csv':
            LOGGER.info('Reading CSV file %s', filename)
            data = pd.read_csv(filename, dtype=str)
        elif extension == 'feather':
            LOGGER.info('Reading Feather file %s', filename)
            data = pd.read_feather(filename)
        else:
            raise ValueError(f"unknown file extension '{extension}'")

        if data.empty:
            raise ValueError(f"No data loaded from file {filename}")

        if self._expected_df_lengths:
            cls._assert_reasonable_dataframe_length(getattr(self._expected_df_lengths.entity, key), data)

        return data

    @classmethod
    def _assert_reasonable_dataframe_length(cls, expected_df_length, data):
        length_delta = abs(expected_df_length - len(data))
        deviation = length_delta / expected_df_length
        arbitrary_max_deviation = 0.25

        if deviation > arbitrary_max_deviation:
            raise InvalidDataException('The following DataFrame has an unusual length: %s', data)