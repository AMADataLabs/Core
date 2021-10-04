""" Address Load Aggregation Transformer """
from datetime import datetime
from io import BytesIO
import logging
from string import ascii_uppercase, digits
import pandas as pd
import pickle as pk

from datalabs.etl.transform import TransformerTask  # pylint: disable=import-error

# pylint: disable=bare-except,logging-fstring-interpolation

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel('INFO')


# address load files MUST HAVE THESE COLUMNS (but values for some are optional)
REQUIRED_COLUMNS = [
    'entity_id', 'me#', 'comm_id', 'usage', 'load_type_ind', 'addr_type',
    'addr_line_1', 'addr_line_2', 'addr_line_3', 'addr_city', 'addr_state',
    'addr_zip', 'addr_plus4', 'addr_country', 'source', 'source_dtm'
]
# subset of required columns which MUST have values -- NON-OPTIONAL
REQUIRED_NON_NULL_COLUMNS = [
    'usage', 'load_type_ind', 'addr_type', 'addr_line_1', 'addr_city',
    'addr_state', 'addr_zip', 'source', 'source_dtm'
]


def _process_aggregate_data(aggregate_data: pd.DataFrame):
    """
    Would be inaccurate/redundant to set multiple addresses with the same usage to a single physician,
    so this function identifies which records are unique by (individual, usage) and which are not.
    """
    if 'filename' in aggregate_data.columns.values:
        aggregate_data.drop(columns=['filename'], axis=1, inplace=True)
    data = aggregate_data.copy().drop_duplicates()
    me_counts = data[~data['me#'].apply(_isna)].groupby(by=['me#', 'usage']).size()
    entity_counts = data[~data['entity_id'].apply(_isna)].groupby(by=['entity_id', 'usage']).size()

    multiples_me = me_counts[me_counts > 1].dropna()
    multiples_entity_id = entity_counts[entity_counts > 1]

    reindexed_me = data[~data['me#'].apply(_isna)].set_index(['me#', 'usage'])
    reindexed_entity_id = data[~data['entity_id'].apply(_isna)].set_index(['entity_id', 'usage'])

    # valid_data is data where the me+usage key or entity_id+usage key is unique
    valid_data = pd.concat(
        [
            reindexed_me[~reindexed_me.index.isin(multiples_me.index)].reset_index(),
            reindexed_entity_id[~reindexed_entity_id.index.isin(multiples_entity_id.index)].reset_index()
        ],
        ignore_index=True
    ).drop_duplicates()

    invalid_data = pd.concat(
        [
            reindexed_me[reindexed_me.index.isin(multiples_me.index)].reset_index(),
            reindexed_entity_id[reindexed_entity_id.index.isin(multiples_entity_id.index)].reset_index()
        ],
        ignore_index=True
    ).drop_duplicates()

    LOGGER.info(f"AGGREGATE DATA - VALID: {str(len(valid_data))}\t\tINVALID: {str(len(invalid_data))}")

    return valid_data, invalid_data


def _is_valid_component_data_structure(data: pd.DataFrame):
    is_valid = True
    columns = data.columns.values
    missing_columns = []
    for col in REQUIRED_COLUMNS:
        if col not in columns:
            is_valid = False  # required column not found in dataframe
            missing_columns.append(col)
    if len(missing_columns) > 0:
        LOGGER.info(f"MISSING COLUMNS: {str(missing_columns)}")
    if len(columns) > len(REQUIRED_COLUMNS):
        LOGGER.info(f"REQUIRED COLUMNS: {str(REQUIRED_COLUMNS)}")
        LOGGER.info(f"FOUND COLUMNS: {str(columns)}")
        is_valid = False  # more columns found than required
    return is_valid


def _process_component_data(data: pd.DataFrame):
    """
    Validates structure of component data files -- columns
    """
    for col in data.columns.values:
        data[col] = data[col].fillna('').astype(str).apply(lambda x: x.strip())

    is_valid_structure = _is_valid_component_data_structure(data)

    if not is_valid_structure:
        LOGGER.info('INVALID DATA STRUCTURE')
        LOGGER.info(data.columns.values)
        valid_data = None
        invalid_data = data
    else:
        valid_data = _get_valid_rows(data)
        # invalid_data is data with erroneous row data, found where entity or ME # not found in filtered valid data
        invalid_data = data[
            (~data['me#'].isin(valid_data['me#'])) |
            (~data['entity_id'].isin(valid_data['entity_id']))
        ]
    return valid_data, invalid_data


def _get_valid_rows(data: pd.DataFrame):
    valid_data = data.copy()
    valid_data = valid_data[valid_data['usage'].apply(_is_valid_usage)]
    valid_data = valid_data[valid_data['addr_zip'].apply(_is_valid_zip)]
    valid_data = valid_data[valid_data['load_type_ind'].apply(_is_valid_load_type_ind)]
    valid_data = valid_data[valid_data['addr_state'].apply(_is_valid_state)]
    valid_data = valid_data[valid_data['source_dtm'].apply(_is_valid_date)]
    valid_data = valid_data[valid_data['addr_type'].apply(_is_valid_addr_type)]

    valid_rows = []
    for _, row in valid_data.iterrows():
        is_valid_row = _is_valid_row(row)

        if is_valid_row:
            valid_rows.append(row)
    valid_data = pd.concat(valid_rows, ignore_index=True, axis=1).T
    valid_data['source_dtm'] = pd.to_datetime(valid_data['source_dtm'])
    return valid_data


def _is_valid_row(row):
    is_valid_row = True
    # entity_id OR me# must exist
    if _isna(row['entity_id']) and _isna(row['me#']):
        is_valid_row = False

    for col in REQUIRED_NON_NULL_COLUMNS:
        if _isna(row[col]):
            is_valid_row = False  # column exists in file but has a null value
    return is_valid_row


def _isna(text):
    return text in [None, '', 'nan', 'null', 'none', '.', '-']


def _is_valid_entity_id(val):
    try:
        return str(val).isdigit()
    except:
        return False


def _is_valid_me_number(val):
    try:
        return len(val) == 11 and isinstance(val, str) and all(x.isdigit() for x in val)
    except:
        return False


def _is_valid_usage(val):
    try:
        return val in ['PP', 'PO']
    except:
        return False


def _is_valid_zip(val):
    try:
        return len(str(val)) in (4, 5) and all(str(x) in digits for x in val)
    except:
        return False


def _is_valid_load_type_ind(val):
    try:
        return val in ('R', 'A', 'D')
    except:
        return False


def _is_valid_state(val):
    try:
        return isinstance(val, str) and len(val) == 2 and all(x in ascii_uppercase for x in val)
    except:
        return False


# pylint: disable=unused-argument
def _is_valid_addr_type(val):
    try:
        # return val in ('N', 'OF', 'HO', 'H', 'GROUP')  # unsure about rules, figure out later
        return True
    except:
        return False


def _is_valid_date(val):
    try:
        if not isinstance(val, datetime):
            pd.to_datetime(val)  # should be able to cast
        return True
    except:
        return False


def _reorder_batch_load_column_order(data: pd.DataFrame):
    batch_data = pd.DataFrame()
    for col in REQUIRED_COLUMNS:
        batch_data[col] = data[col]
    return batch_data


class AddressLoadFileAggregationTransformerTask(TransformerTask):
    def _transform(self) -> 'Transformed Data':
        # dataframes = [pd.read_csv(BytesIO(data)) for data in self._parameters['data']]
        dataframes = [pd.read_csv(BytesIO(data[1])) for data in pk.loads(self._parameters['data'][0])]
        valid_dataframe_list = []
        invalid_dataframe_list = []

        for data in dataframes:
            valid_data, invalid_data = _process_component_data(data=data)
            LOGGER.info(f'VALID: {str(len(valid_data) if valid_data is not None else 0)}')
            LOGGER.info(f'INVALID: {str(len(invalid_data) if invalid_data is not None else 0)}')

            if valid_data is not None:
                valid_dataframe_list.append(valid_data)

            if invalid_data is not None:
                invalid_dataframe_list.append(invalid_data)

        if len(valid_dataframe_list) == 0:
            valid_aggregate_data = pd.DataFrame()
            invalid_aggregate_data = pd.concat(invalid_dataframe_list)
        else:
            aggregate_data = pd.concat(valid_dataframe_list, ignore_index=True)
            valid_aggregate_data, invalid_aggregate_data = _process_aggregate_data(aggregate_data=aggregate_data)

        valid_csv = BytesIO()
        invalid_csv = BytesIO()

        valid_aggregate_data.to_csv(valid_csv, index=False)
        invalid_aggregate_data.to_csv(invalid_csv, index=False)

        return [valid_csv.getvalue(), invalid_csv.getvalue()]
