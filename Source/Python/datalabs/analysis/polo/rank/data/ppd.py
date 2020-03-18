from   collections import namedtuple
import logging
from   pathlib import Path
import pickle

import pandas as pd

from   datalabs.analysis.polo.rank.data.entity import EntityTableCleaner


ModelInputData = namedtuple('ModelInputData', 'model ppd entity date')
ModelOutputData = namedtuple('ModelOutputData', 'predictions ranked_predictions')
EntityData = namedtuple('EntityData', 'entity_comm_at entity_comm_usg post_addr_at license_lt entity_key_et')
ModelParameters = namedtuple('ModelParameters', 'meta variables')

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class InputDataLoader():
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

    @classmethod
    def _get_ppd_data(cls, ppd_file: str) -> pd.DataFrame:
        LOGGER.info('--- Loading PPD Data ---')

        LOGGER.info('Reading CSV file %s', ppd_file)
        ppd_data = pd.read_csv(ppd_file, dtype=str)

        return ppd_data

    @classmethod
    def _get_entity_data(cls, entity_files: EntityData) -> EntityData:
        LOGGER.info('--- Loading Entity Data ---')

        return EntityData(
            entity_comm_at=cls._extract_entity_data_from_file(entity_files.entity_comm_at),
            entity_comm_usg=cls._extract_entity_data_from_file(entity_files.entity_comm_usg),
            post_addr_at=cls._extract_entity_data_from_file(entity_files.post_addr_at),
            license_lt=cls._extract_entity_data_from_file(entity_files.license_lt),
            entity_key_et=cls._extract_entity_data_from_file(entity_files.entity_key_et),
        )

    @classmethod
    def _extract_entity_data_from_file(cls, filename):
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

        return data
