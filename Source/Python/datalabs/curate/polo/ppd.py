""" Classes for loading PPD for POLO analysis """
import logging
import pickle

import pandas as pd

from   datalabs.analysis.exception import InvalidDataException
from   datalabs.analysis.polo.model import ModelInputData, ModelVariables, EntityData

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

class InputDataLoader():
    def __init__(self, expected_df_lengths: ModelInputData = None):
        self._expected_df_lengths = expected_df_lengths

    def load(self, input_files: ModelInputData) -> ModelInputData:
        model = self._load_model(input_files.model)
        variables = self._get_variables(input_files.variables, model)
        ppd_data = self._load_ppd_data(input_files.ppd)
        entity_data = self._load_entity_data(input_files.entity)

        return ModelInputData(
            model=model,
            variables=variables,
            ppd=ppd_data,
            entity=entity_data,
            date=input_files.date
        )

    @classmethod
    def _load_model(cls, model_file: str) -> 'XGBClassifier':
        LOGGER.info('-- Loading Model Parameters --')

        LOGGER.info('Reading Pickle file %s', model_file)
        return pickle.load(open(model_file, 'rb'))

    @classmethod
    def _get_variables(cls, variables, model):
        return ModelVariables(
            input=variables.input,
            feature=model.get_booster().feature_names,
            output=variables.output,
        )

    def _load_ppd_data(self, ppd_file: str) -> pd.DataFrame:
        LOGGER.info('--- Loading PPD Data ---')

        LOGGER.info('Reading CSV file %s', ppd_file)
        ppd_data = pd.read_csv(ppd_file, dtype=str)

        if self._expected_df_lengths:
            self._assert_reasonable_dataframe_length(self._expected_df_lengths.ppd, ppd_data)

        return ppd_data

    def _load_entity_data(self, entity_files: EntityData) -> EntityData:
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
            self._assert_reasonable_dataframe_length(getattr(self._expected_df_lengths.entity, key), data)

        return data

    @classmethod
    def _assert_reasonable_dataframe_length(cls, expected_df_length, data):
        length_delta = abs(expected_df_length - len(data))
        deviation = length_delta / expected_df_length
        arbitrary_max_deviation = 0.25
        LOGGER.info('Record count: %d. Deviation: %.2f %%', len(data), deviation*100)

        if deviation > arbitrary_max_deviation:
            raise InvalidDataException(f'The following DataFrame has an unusual length: {data}')
