""" Common data processing functions """
# pylint: disable=singleton-comparison
from   datetime import datetime
import logging
import re

import numpy as np
import pandas as pd

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def get_active_polo_eligible_addresses(base_data, path_to_entity_comm_at_file, path_to_post_addr_at_file, as_of_date):
    entity_comm_data = load_processed_data(path_to_entity_comm_at_file, as_of_date, 'BEGIN_DT', 'END_DT')
    post_addr_data = load_processed_data(path_to_post_addr_at_file)
    entity_comm_data = add_address_key(entity_comm_data, post_addr_data)
    # entity_comm_at file should already be filtered to polo-eligible sources and types, just need to filter to active

    base_data = base_data.merge(entity_comm_data, on='ENTITY_ID')

    base_data = base_data[base_data['ACTIVE'] == True]

    return base_data


def keep_alphanumeric(text):
    keep_text = ''

    if isinstance(text, str):
        keep_text = re.sub(r"[^0-9a-zA-Z_\- ]", "", text)

    return keep_text


def clean_zip(address_key):
    result = address_key
    tokens = address_key.split('_')
    suffix = tokens[-1]
    prefix = ' '.join(tokens[:-1])

    if len(suffix) >= 5:
        result = f"{prefix}_{suffix[:5]}"

    return result


def get_memory_usage(data: pd.DataFrame):
    usage = data.memory_usage().sum() / (1024 ** 2)

    return round(usage, 2)


def add_column_prefixes(data: pd.DataFrame, prefix: str, exclude_columns=None):
    columns = []

    for column in data.columns.values:
        if column in exclude_columns:
            columns.append(column)
        else:
            columns.append(f"{prefix}_{column}")

    data.columns = columns


def load_active_processed_data(
        data_or_path_to_file,
        as_of_date=None,
        begin_date_column=None,
        end_date_column=None
):
    data = load_processed_data(data_or_path_to_file, as_of_date, begin_date_column, end_date_column)

    log_info(f"\tFILTERING TO ACTIVE ONLY START: {data.shape[0]}")
    data = data[data['ACTIVE'] == True]
    log_info(f"\tFILTERING TO ACTIVE ONLY END: {data.shape[0]}")

    return data


def load_processed_data(
        data_or_path_to_file,
        as_of_date=None,
        begin_date_column=None,
        end_date_column=None
):
    data = data_or_path_to_file

    if isinstance(data_or_path_to_file, str):
        data = pd.read_csv(data_or_path_to_file, sep='|', dtype=str)

    rename_columns_in_uppercase(data)

    if begin_date_column not in data.columns.values or end_date_column not in data.columns.values:
        raise ValueError(f"Missing {begin_date_column} and/or {end_date_column} column(s).")

    if all(x is not None for x in (as_of_date, begin_date_column, end_date_column)):
        data = resolve_dates(data, begin_date_column, end_date_column, as_of_date)

        data = set_active_indicator(data, end_date_column, as_of_date)

    return data


def add_address_key(data: pd.DataFrame, post_addr_at_data: pd.DataFrame):
    data = data.merge(post_addr_at_data, on='COMM_ID', how='left')
    return data


def rename_columns_in_uppercase(data: pd.DataFrame):
    columns = [column.upper() for column in data.columns.values]
    data.columns = columns


def resolve_dates(data: pd.DataFrame, begin_date_column: str, end_date_column, as_of_date: str = 'YYYY-MM-DD'):
    as_of_date = datetime.strptime(as_of_date, '%Y-%m-%d')

    for column in [begin_date_column, end_date_column]:
        data[column] = pd.to_datetime(data[column], errors='coerce')

    data = data[data[begin_date_column] <= as_of_date]  # data must have already began by as_of_date
    assert data.shape[0] > 0, 'Something went wrong in filtering data ahead of as_of_date, no data remains'

    # if end_date column is populated but AFTER the as_of_date, replace with null (to mark as active)
    data.loc[data[end_date_column] >= as_of_date, end_date_column] = np.nan

    return data


def set_active_indicator(data, end_date_column, as_of_date):
    data.loc[(data[end_date_column].isna()) | (data[end_date_column] >= as_of_date), 'ACTIVE'] = True

    data.loc[data['ACTIVE'] != True, 'ACTIVE'] = False

    return data


def log_info(*message):
    now = str(datetime.now())[:19]
    log_message = f"{now}\t{' '.join(str(m) for m in message)}"
    LOGGER.info(log_message)
