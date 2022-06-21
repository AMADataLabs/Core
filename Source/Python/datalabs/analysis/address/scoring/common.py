""" Common data processing functions """
# pylint: disable=singleton-comparison
from datetime import datetime
import logging
import numpy as np
import pandas as pd


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def log_info(*message):
    now = str(datetime.now())[:19]
    log_message = f"{now}\t{' '.join(str(m) for m in message)}"
    LOGGER.info(log_message)


def rename_columns_in_uppercase(data: pd.DataFrame):
    columns = [column.upper() for column in data.columns.values]
    data.columns = columns


def add_column_prefixes(data: pd.DataFrame, prefix: str, exclude_cols=None):
    cols = []
    for col in data.columns.values:
        if col in exclude_cols:
            cols.append(col)
        else:
            cols.append(f"{prefix}_{col}")
    data.columns = cols


def resolve_data_date(data: pd.DataFrame, begin_date_column: str, end_date_column, as_of_date: str = 'YYYY-MM-DD'):
    assert begin_date_column in data.columns.values
    assert end_date_column in data.columns.values

    as_of_date = datetime.strptime(as_of_date, '%Y-%m-%d')

    for column in [begin_date_column, end_date_column]:
        data[column] = pd.to_datetime(data[column], errors='coerce')

    data = data[data[begin_date_column] <= as_of_date]  # data must have already began by as_of_date
    assert data.shape[0] > 0, 'Something went wrong in filtering data ahead of as_of_date, no data remains'

    # if end_date column is populated but AFTER the as_of_date, replace with null (to mark as active)
    data.loc[data[end_date_column] >= as_of_date, end_date_column] = np.nan

    return data


def load_processed_data(path_to_file, as_of_date=None, begin_date_column=None, end_date_column=None):
    data = pd.read_csv(path_to_file, sep='|', dtype=str)
    rename_columns_in_uppercase(data)
    if as_of_date is not None and begin_date_column is not None and end_date_column is not None:
        data = resolve_data_date(
            data,
            as_of_date=as_of_date,
            begin_date_column=begin_date_column,
            end_date_column=end_date_column
        )
        data.loc[
            (data[end_date_column].isna()) |
            (data[end_date_column] >= as_of_date),
            'ACTIVE'
        ] = True
        data.loc[data['ACTIVE'] != True, 'ACTIVE'] = False
    log_info(f"\t{path_to_file.split('/')[-1]} ~~~ {get_memory_usage(data)} MB")
    return data


def add_address_key(data: pd.DataFrame, post_addr_at_data: pd.DataFrame):
    data = data.merge(post_addr_at_data, on='COMM_ID', how='left')
    return data


def get_memory_usage(data: pd.DataFrame):
    usage = data.memory_usage().sum() / (1024 ** 2)
    usage = round(usage, 2)
    return usage


def get_active_polo_eligible_addresses(base_data, path_to_entity_comm_at_file, path_to_post_addr_at_file, as_of_date):
    entity_comm_data = load_processed_data(path_to_entity_comm_at_file, as_of_date, 'BEGIN_DT', 'END_DT')
    post_addr_data = load_processed_data(path_to_post_addr_at_file)
    entity_comm_data = add_address_key(entity_comm_data, post_addr_data)
    # entity_comm_at file should already be filtered to polo-eligible sources and types, just need to filter to active
    base_data = base_data.merge(entity_comm_data, on='ENTITY_ID')
    base_data = base_data[base_data['ACTIVE'] == True]
    return base_data
