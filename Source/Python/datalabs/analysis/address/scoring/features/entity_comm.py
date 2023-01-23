""" Adds address-based features to a dataset utilizing the ENTITY_COMM_AT table from AIMS """

# REQUIRED BASE INPUT COLUMNS
#    - ENTITY_ID    (physician ID from AIMS)
#    - COMM_ID      (address ID from AIMS)

from   dataclasses import dataclass
from   datetime import datetime
import logging
import os
import warnings

import pandas as pd
from   tqdm import tqdm

from datalabs.analysis.address.scoring.common import load_processed_data, log_info
from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task


warnings.filterwarnings('ignore', '.*A value is trying to be set on a copy of a slice from a DataFrame.*')
warnings.filterwarnings('ignore', '.*SettingWithCopyWarning*')
warnings.filterwarnings('ignore', '.*FutureWarning*')

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class EntityCommFeatureGenerationTransformerParameters:
    as_of_date: str
    execution_time: str = None


class EntityCommFeatureGenerationTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = EntityCommFeatureGenerationTransformerParameters

    def run(self) -> 'list<bytes>':
        base_data, entity_comm = [self._csv_to_dataframe(d, sep='|', dtype=str) for d in cls._data]
        as_of_date = self._parameters.as_of_date

        features = self._add_entity_comm_at_features(base_data, entity_comm, as_of_date)

        return [cls._dataframe_to_csv(features, sep='|')]

    @classmethod
    def _add_entity_comm_at_features(base_data, data_or_path_to_entity_comm_at_file, as_of_date, save_dir=None):
        base_data.columns = [col.upper() for col in base_data.columns]
        entity_comm_data = load_processed_data(data_or_path_to_entity_comm_at_file, as_of_date, 'BEGIN_DT', 'END_DT')

        entity_comm_data = entity_comm_data[
            (entity_comm_data['ENTITY_ID'].isin(base_data['ENTITY_ID'].values)) |
            (entity_comm_data['COMM_ID'].isin(base_data['COMM_ID'].values))
        ]

        log_info('\tENTITY_COMM - Address Age')
        features = cls._add_feature_address_age(base_data, entity_comm_data, as_of_date)
        log_info('\tENTITY_COMM - Physician Active Address Counts')
        features = cls._add_feature_physician_num_active_addresses(features, entity_comm_data)
        log_info('\tENTITY_COMM - Address Active Frequency')
        features = cls._add_feature_active_address_total_frequency(features, entity_comm_data)
        log_info('\tENTITY_COMM - Newer Address Counts')
        features = cls._add_feature_physician_how_many_newer_addresses(features, entity_comm_data)
        log_info('\tENTITY_COMM - Address Sources')
        features = cls._add_feature_address_sources(features, entity_comm_data)

        log_info('BASE_DATA MEMORY:', features.memory_usage().sum() / 1024 ** 2)
        if save_dir is not None:
            save_filename = os.path.join(save_dir, F'features__entity_comm__{as_of_date}.txt')
            log_info(f'SAVING ENTITY_COMM FEATURES: {save_filename}')
            features.to_csv(save_filename, sep='|', index=False)

        return features

    @classmethod
    def cls._add_feature_address_age(cls, base_data: pd.DataFrame, entity_comm_at_data: pd.DataFrame, as_of_date: str):
        """ Get age of addresses in years """
        if isinstance(as_of_date, str):
            as_of_date = datetime.strptime(as_of_date, '%Y-%m-%d')
        assert isinstance(as_of_date, datetime)

        address_age_data = entity_comm_at_data[['ENTITY_ID', 'COMM_ID', 'BEGIN_DT']].sort_values(by='BEGIN_DT').groupby(
            ['ENTITY_ID', 'COMM_ID']
        ).first().reset_index()

        address_age_data['ENTITY_COMM_ADDRESS_AGE'] = as_of_date - address_age_data['BEGIN_DT']
        address_age_data['ENTITY_COMM_ADDRESS_AGE'] = address_age_data['ENTITY_COMM_ADDRESS_AGE'].apply(
            lambda x: x.days / 365
        )
        address_age_data['ENTITY_COMM_ADDRESS_AGE'].drop(columns=['BEGIN_DT'], inplace=True)

        base_data = base_data.merge(address_age_data, on=['ENTITY_ID', 'COMM_ID'], how='left')

        return base_data

    @classmethod
    def cls._add_feature_physician_num_active_addresses(
        cls,
        base_data: pd.DataFrame,
        entity_comm_at_data: pd.DataFrame
    ):
        """ Get the number of active addresses per physician """
        data = entity_comm_at_data[['ENTITY_ID', 'COMM_ID', 'END_DT']][entity_comm_at_data['END_DT'].isna()]
        data = data[data['ENTITY_ID'].isin(base_data['ENTITY_ID'].values)]
        data = data[['ENTITY_ID', 'COMM_ID']].drop_duplicates()
        # del data['END_DT']
        address_counts = data.groupby('ENTITY_ID').size().reset_index().rename(columns={0: 'ENTITY_COMM_ACTIVE_ADDRESSES'})
        address_counts['ENTITY_ID'] = address_counts['ENTITY_ID'].astype(str)
        base_data = base_data.merge(address_counts, on='ENTITY_ID', how='left')

        return base_data

    @classmethod
    def cls._add_feature_address_sources(cls, base_data: pd.DataFrame, entity_comm_at_data: pd.DataFrame):
        """ Creates boolean flags for physician-address pairs for each address source """
        data = entity_comm_at_data[['ENTITY_ID', 'COMM_ID', 'SRC_CAT_CODE']].drop_duplicates()
        data = data[
            (data['ENTITY_ID'].isin(base_data['ENTITY_ID'].values)) &
            (data['COMM_ID'].isin(base_data['COMM_ID'].values))
        ]

        sources_found = data['SRC_CAT_CODE'].dropna().drop_duplicates()

        log_info('\tCreating initial source flags...')
        for source in tqdm(sources_found):
            # create boolean flags
            source_feature_column = f"ENTITY_COMM_SRC_CAT_CODE_{source}"
            data[source_feature_column] = data['SRC_CAT_CODE'] == source
            data[source_feature_column] = data[source_feature_column].astype(int)

        log_info('\tAggregating source flags per physician-address pair...')
        grouped = data.groupby(['ENTITY_ID', 'COMM_ID']).sum().reset_index()

        ### # slower but less memory-intensive method, saved in case we run into memory usage errors
        ### grouped = data.groupby(['ENTITY_ID', 'COMM_ID'])
        ### for source in tqdm(sources_found):
        ###     source_feature_column = f"ENTITY_COMM_SRC_CAT_CODE_{source}"
        ###     # aggregate flags to a single row per ENTITY_ID + COMM_ID and add to base data
        ###     source_group = grouped[source_feature_column].sum().reset_index()
        ###     base_data = base_data.merge(source_group, how='left')

        base_data = base_data.merge(grouped, how='left')

        return base_data

    @classmethod
    def cls._add_feature_active_address_total_frequency(
        cls,
        base_data: pd.DataFrame,
        entity_comm_at_data: pd.DataFrame
    ):
        """ Counts the appearances of an address in the active DPC address universe """
        data = entity_comm_at_data[entity_comm_at_data['COMM_ID'].isin(
            base_data['COMM_ID'].values)
        ][['ENTITY_ID', 'COMM_ID', 'END_DT']].drop_duplicates()
        data = data[data['END_DT'].isna()]
        del data['END_DT']
        data = data[['ENTITY_ID', 'COMM_ID']].drop_duplicates().groupby('COMM_ID').size().reset_index().rename(
            columns={0: 'ENTITY_COMM_ADDRESS_ACTIVE_FREQUENCY'}
        )
        base_data = base_data.merge(data, on='COMM_ID', how='left')
        base_data['ENTITY_COMM_ADDRESS_ACTIVE_FREQUENCY'] = base_data['ENTITY_COMM_ADDRESS_ACTIVE_FREQUENCY'].fillna(0.0)

        return base_data

    @classmethod
    def cls._add_feature_physician_how_many_newer_addresses(
        cls,
        base_data: pd.DataFrame,
        entity_comm_at_data: pd.DataFrame
    ):
        """ Counts the number of active office addresses this physician has on record """
        data = entity_comm_at_data[
            (entity_comm_at_data['COMM_ID'].isin(base_data['COMM_ID'].values)) &
            (entity_comm_at_data['ENTITY_ID'].isin(base_data['ENTITY_ID'].values))
        ]
        data = data[data['ACTIVE'] == True]
        data = data[['ENTITY_ID', 'COMM_ID', 'BEGIN_DT']].drop_duplicates()

        data.sort_values(by='BEGIN_DT', ascending=False, inplace=True)
        groups = data.groupby('ENTITY_ID')

        results = []
        for entity_id, group in tqdm(groups, total=data['ENTITY_ID'].nunique()):
            for i, row in group.iterrows():
                comm_id = row['COMM_ID']
                n_new = i
                results.append({'ENTITY_ID': entity_id, 'COMM_ID': comm_id, 'N_NEWER_ADDRESSES': n_new})

        results = pd.DataFrame(results)
        base_data = base_data.merge(results, on=['ENTITY_ID', 'COMM_ID'], how='left')

        return base_data
