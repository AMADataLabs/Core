""" Adds address-based features to a dataset utilizing the ENTITY_COMM_AT table from AIMS """

# REQUIRED BASE INPUT COLUMNS
#    - ENTITY_ID    (physician ID from AIMS)
#    - COMM_ID      (address ID from AIMS)

# pylint: disable=import-error, unused-import, singleton-comparison

from datetime import datetime
import gc
import logging
import os
import warnings
import pandas as pd
from tqdm import tqdm
from datalabs.analysis.address.scoring.common import load_processed_data, log_info

warnings.filterwarnings('ignore', '.*A value is trying to be set on a copy of a slice from a DataFrame.*')
warnings.filterwarnings('ignore', '.*SettingWithCopyWarning*')
warnings.filterwarnings('ignore', '.*FutureWarning*')

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def add_entity_comm_usg_at_features(
        base_data,
        path_to_entity_comm_usg_at_file,
        as_of_date,
        save_dir):
    entity_comm_usg_data = load_processed_data(path_to_entity_comm_usg_at_file, as_of_date, 'USG_BEGIN_DT', 'END_DT')

    log_info('\tENTITY_COMM_USG - comm_id comm_usg counts')
    features = add_feature_comm_id_usage_counts(base_data, entity_comm_usg_data)

    log_info('BASE_DATA MEMORY:', features.memory_usage().sum() / 1024 ** 2)

    save_filename = os.path.join(save_dir, f'features__entity_comm_usg__{as_of_date}.txt')
    log_info(f'SAVING ENTITY_COMM FEATURES: {save_filename}')
    features.to_csv(save_filename, sep='|', index=False)


def flatten_usage_counts(entity_comm_usg_data: pd.DataFrame, active: bool):
    """
    active: bool - whether entity_comm_usg_data was filtered to only contain ACTIVE usage data
                 - if True, will flag feature column as 'ACTIVE', otherwise 'HISTORY'
    """
    if active:
        flag = 'ACTIVE'
    else:
        flag = 'HISTORY'
    counts_df = entity_comm_usg_data[
        ['ENTITY_ID', 'COMM_ID', 'COMM_USAGE']
    ].drop_duplicates().groupby(['COMM_ID', 'COMM_USAGE']).size().reset_index().rename(columns={0: 'COUNT'})

    flattened = {}
    for _, row in tqdm(counts_df.iterrows(), total=counts_df.shape[0]):
        comm_id = row['COMM_ID']
        usage = row['COMM_USAGE']
        count = row['COUNT']
        if not comm_id in flattened:
            flattened[comm_id] = {'COMM_ID': comm_id}
        flattened[comm_id][f"ENTITY_COMM_USG_COMM_ID_COMM_USAGE_COUNTS_{flag}_{usage}"] = count
    del counts_df
    gc.collect()
    flattened_dict_data = [data for comm_id, data in flattened.items()]
    flattened_df = pd.DataFrame(flattened_dict_data)

    return flattened_df


def add_feature_comm_id_usage_counts(base_data: pd.DataFrame, entity_comm_usg_data: pd.DataFrame):
    """ Gets the ACTIVE and HISTORICAL counts of each usage a given comm_id has *throughout the physician universe*
        It's important to NOT include physician-level considerations here, because a POLO will have particular usages in
        the entity_comm_usg data which will set it apart from non-POLO addresses. To keep the model "blind" to actual
        POLO status information, we need to keep the features similar for POLO and non-POLO addresses. This means we
        should ignore entity_id - comm_id pair information and only use information that could be found for ANY address,
        POLO or not.
    """
    print('p1', entity_comm_usg_data.shape[0])
    print(entity_comm_usg_data.memory_usage().sum() / 1024 ** 2)
    entity_comm_usg_data = entity_comm_usg_data[entity_comm_usg_data['COMM_ID'].isin(base_data['COMM_ID'].values)]
    print('p2', entity_comm_usg_data.shape[0])
    print(entity_comm_usg_data.memory_usage().sum() / 1024 ** 2)

    data_active = entity_comm_usg_data[
        entity_comm_usg_data['ACTIVE'] == True
        ]
    flattened_active = flatten_usage_counts(data_active, active=True).fillna(0)
    del data_active
    gc.collect()
    flattened_historical = flatten_usage_counts(entity_comm_usg_data, active=False).fillna(0)
    features = flattened_active.merge(flattened_historical, on='COMM_ID', how='left').fillna(0)
    return features
