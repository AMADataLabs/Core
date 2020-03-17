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


class EntityCommAtCleaner(EntityTableCleaner):
    def __init__(self, input_path, output_path):
        column_names = 'entity_id', 'comm_type', 'begin_dt', 'comm_id', 'end_dt', 'src_cat_code'
        column_filters = {name:'ent_comm_'+name for name in column_names}

        super().__init__(
            input_path,
            output_path,
            row_filters={'comm_cat': 'A '},
            column_filters=column_filters,
            types={'entity_id': 'uint32', 'comm_id': 'uint32'},
            datestamp_columns=['begin_dt', 'end_dt']
        )


class EntityCommUsgCleaner(EntityTableCleaner):
    def __init__(self, input_path, output_path):
        column_names = ['entity_id', 'comm_type', 'comm_usage', 'usg_begin_dt', 'comm_id', 'comm_type',
                        'end_dt', 'src_cat_code']
        column_filters = {name:'usg_'+name for name in column_names}
        column_filters['usg_begin_dt'] == 'usg_begin_dt'

        super().__init__(
            input_path,
            output_path,
            row_filters={'comm_cat': 'A '},
            column_filters=column_filters,
            types={'entity_id': 'uint32', 'comm_id': 'uint32'},
            datestamp_columns=['usg_begin_dt', 'end_dt']
        )


class PostAddrAtCleaner(EntityTableCleaner):
    def __init__(self, input_path, output_path):
        column_names = ['comm_id', 'addr_line2', 'addr_line1', 'addr_line0', 'city_cd',
                        'state_cd', 'zip', 'plus4']
        column_filters = {name:'post_'+name for name in column_names}

        super().__init__(
            input_path,
            output_path,
            column_filters=column_filters,
            types={'comm_id': 'uint32'}
        )


class LicenseLtCleaner(EntityTableCleaner):
    def __init__(self, input_path, output_path):
        super().__init__(
            input_path,
            output_path,
            types={'entity_id': 'uint32', 'comm_id': 'uint32'},
            datestamp_columns=['lic_exp_dt', 'lic_issue_dt', 'lic_rnw_dt']
        )

    def _clean_values(self, table):
        table = super()._clean_values(table)
        table = self._insert_default_comm_id(table)

        return table

    @classmethod
    def _insert_default_comm_id(cls, table):
        table['comm_id'].fillna('0', inplace=True)

        return table


class EntityKeyEtCleaner(EntityTableCleaner):
    def __init__(self, input_path, output_path):
        super().__init__(
            input_path,
            output_path,
            types={'entity_id': 'uint32'}
        )


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
