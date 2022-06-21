""" Adds address-based features to a dataset utilizing the LICENSE_LT table from AIMS """

# REQUIRED BASE INPUT COLUMNS
#    - ENTITY_ID    (physician ID from AIMS)
#    - COMM_ID      (address ID from AIMS)
#    - ADDRESS_STATE (from POST_ADDR_AT in AIMS
#    - AS_OF_DATE

# pylint: disable=import-error, unused-import, singleton-comparison

from datetime import datetime
import logging
import warnings
import pandas as pd
from tqdm import tqdm
from datalabs.analysis.address.scoring.common import add_column_prefixes, load_processed_data, log_info

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

warnings.filterwarnings('ignore', '.*A value is trying to be set on a copy of a slice from a DataFrame.*')
warnings.filterwarnings('ignore', '.*SettingWithCopyWarning*')
warnings.filterwarnings('ignore', '.*FutureWarning*')


def add_license_features(base_data: pd.DataFrame, path_to_license_file, path_to_post_addr_file, as_of_date):
    log_info('LOADING LICENSE DATA', path_to_license_file)
    license_data = load_processed_data(path_to_license_file, as_of_date, 'LIC_ISSUE_DT', 'LIC_EXP_DT')
    log_info('LOADING POST_ADDR DATA', path_to_post_addr_file)
    post_addr_data = load_processed_data(path_to_post_addr_file, as_of_date)
    log_info('ADDING ADDRESS DATA TO LICENSE DATA')
    license_data = merge_license_address_data(license_data, post_addr_data)
    del post_addr_data
    log_info('ADD FEATURE ACTIVE LICENSES NEWER/OLDER/MATCH', path_to_post_addr_file)
    base_data = add_feature_active_license_states_newer_older_match(base_data, license_data, as_of_date)
    log_info('ADD FEATURE EXPIRED MATCH', path_to_post_addr_file)
    base_data = add_feature_expired_license_match(base_data, license_data, as_of_date)

    log_info('BASE_DATA MEMORY:', base_data.memory_usage().sum() / 1024 ** 2)
    return base_data


def merge_license_address_data(license_lt_data: pd.DataFrame, post_addr_at_data: pd.DataFrame):
    add_column_prefixes(
        license_lt_data,
        prefix='LICENSE',
        exclude_cols=['ENTITY_ID', 'LIC_ISSUE_DT', 'LIC_EXP_DT']
    )
    add_column_prefixes(
        post_addr_at_data,
        prefix='LICENSE',
        exclude_cols=['STATE_CD']
    )
    license_lt_data = license_lt_data.merge(post_addr_at_data, on='LICENSE_COMM_ID', how='left')
    return license_lt_data


def add_feature_active_license_states_newer_older_match(
        base_data: pd.DataFrame, license_data: pd.DataFrame, as_of_date):
    """ Get boolean flag indicating whether the physician has a previous
    license for a state that's DIFFERENT than this address's state """
    data = license_data[
        (license_data['ENTITY_ID'].isin(base_data['ENTITY_ID'].values)) &
        (license_data['LICENSE_ACTIVE'] == True)
    ]
    # print(data.shape)

    data.sort_values(by='LIC_ISSUE_DT', ascending=False)  # newest first
    data['TIME_LICENSED'] = datetime.strptime(
        as_of_date, '%Y-%m-%d'
    ) - pd.to_datetime(data['LIC_ISSUE_DT'], errors='coerce')
    data['TIME_LICENSED'] = data['TIME_LICENSED'].apply(lambda x: x.days / 365)
    groups = data[
        ['ENTITY_ID', 'LICENSE_COMM_ID', 'LIC_ISSUE_DT', 'LICENSE_STATE_CD', 'TIME_LICENSED']
    ].drop_duplicates().groupby(['ENTITY_ID'])

    # for each state a physician is licensed in, find the following:
    # 1. does the physician have a NEWER active license in another state?
    # 2. does the physician have an OLDER active license in another state?
    results = []
    for entity_id, group in tqdm(groups, total=data['ENTITY_ID'].nunique()):
        group.reset_index(drop=True, inplace=True)
        for i, row in group.iterrows():
            state = row['LICENSE_STATE_CD']
            has_newer = i > 0  # if i > 0, it's not the most recent license (newer exists)
            has_older = i < group.shape[0] - 1  # if we're not at the end of the group, there exist older licenses
            result = {
                'ENTITY_ID': entity_id,
                'LICENSE_STATE_CD': state,
                'HAS_NEWER_ACTIVE_LICENSE_ELSEWHERE': has_newer,
                'HAS_OLDER_ACTIVE_LICENSE_ELSEWHERE': has_older,
                'HAS_ACTIVE_LICENSE_IN_THIS_STATE': True,
                'YEARS_LICENSED_IN_THIS_STATE': as_of_date
            }
            results.append(result)
    results = pd.DataFrame(results)
    results['HAS_NEWER_ACTIVE_LICENSE_ELSEWHERE'] = results['HAS_NEWER_ACTIVE_LICENSE_ELSEWHERE'].fillna(
        True
    ).astype(int)
    results['HAS_OLDER_ACTIVE_LICENSE_ELSEWHERE'] = results['HAS_OLDER_ACTIVE_LICENSE_ELSEWHERE'].fillna(
        True
    ).astype(int)

    base_data = base_data.merge(
        results,
        left_on=['ENTITY_ID', 'STATE_CD'],
        right_on=['ENTITY_ID', 'LICENSE_STATE_CD'],
        how='left'
    )
    base_data['HAS_ACTIVE_LICENSE_IN_THIS_STATE'] = base_data['HAS_ACTIVE_LICENSE_IN_THIS_STATE'].fillna(
        False
    ).astype(int)
    return base_data


def add_feature_expired_license_match(base_data: pd.DataFrame, license_data: pd.DataFrame, as_of_date):
    """ Get boolean flag indicating whether the physician has a previous
    license for a state that's DIFFERENT than this address's state """
    data = license_data[
        (license_data['ENTITY_ID'].isin(base_data['ENTITY_ID'].values)) &
        (license_data['LICENSE_ACTIVE'] == False)
    ]
    data.sort_values(by='LIC_EXP_DT', ascending=False)  # most recent expirations first
    data = data[
        ['ENTITY_ID', 'LICENSE_STATE_CD', 'LIC_EXP_DT']
    ].drop_duplicates().groupby(['ENTITY_ID', 'LICENSE_STATE_CD']).first().reset_index()
    data['LICENSE_THIS_STATE_YEARS_SINCE_EXPIRATION'] = datetime.strptime(
        as_of_date,
        '%Y-%m-%d'
    ) - pd.to_datetime(
        data['LIC_EXP_DT'],
        errors='coerce'
    )
    data['LICENSE_THIS_STATE_YEARS_SINCE_EXPIRATION'] = data['LICENSE_THIS_STATE_YEARS_SINCE_EXPIRATION'].apply(
        lambda x: x.days / 365
    )
    base_data = base_data.merge(
        data,
        left_on=['ENTITY_ID', 'STATE_CD'],
        right_on=['ENTITY_ID', 'LICENSE_STATE_CD'],
        how='left'
    )
    base_data['LICENSE_THIS_STATE_YEARS_SINCE_EXPIRATION'].fillna(0.0)
    return base_data
