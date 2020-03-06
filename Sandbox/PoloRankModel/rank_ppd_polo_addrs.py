# Kari Palmier    7/31/19    Created
# Kari Palmier    8/14/19    Updated to work with more generic get_sample
#
#############################################################################
from   collections import namedtuple
import datetime
import logging
import os
import re
import sys

import dotenv
import pandas as pd

dotenv.load_dotenv()
[sys.path.insert(0, p) for p in os.environ.get('DATALABS_PYTHONPATH', '').split(':')[::-1]]

# from get_ppd import get_latest_ppd_data
from capitalize_column_names import capitalize_column_names
from score_polo_addr_ppd_data import score_polo_ppd_data
from class_model_creation import get_prob_info, get_pred_info
from create_addr_model_input_data import create_ppd_scoring_data

import warnings

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

warnings.filterwarnings("ignore")


InputData = namedtuple('InputData', 'ppd date entity')
EntityData = namedtuple('EntityData', 'entity_comm_at entity_comm_usg post_addr_at license_lt entity_key_et')
ModelData = namedtuple('ModelData', 'model variables')


class InvalidDataException(Exception):
    pass


def main():
    ppd_score_out_dir = os.environ.get('PPD_SCORE_OUT_DIR')

    ppd_archive_dir = ppd_score_out_dir + '_Archived\\'
    if not os.path.exists(ppd_archive_dir):
        os.mkdir(ppd_archive_dir)

    current_time = datetime.datetime.now()
    start_time_str = current_time.strftime("%Y-%m-%d")

    input_data = get_input_data()

    model_data = get_model_data()

    print('Creating scoring data')
    ppd_scoring_df = create_ppd_scoring_data(ppd_df, ppd_date, ent_comm_df, ent_comm_usg_df, post_addr_df,
                                             license_df, ent_key_df)
    assert 'ent_comm_begin_dt' in ppd_scoring_df.columns.values
    print(len(ppd_scoring_df))
    ppd_entity_file = ppd_archive_dir + start_time_str + '_PPD_' + ppd_date_str + '_Polo_Addr_Rank_PPD_Entity_Data.csv'
    print('\tsaving scoring data to {}'.format(ppd_entity_file))
    ppd_scoring_df.to_csv(ppd_entity_file, sep=',', header=True, index=True)

    print('Applying model')
    model_pred_df, model_data_pruned = score_polo_ppd_data(ppd_scoring_df, model, model_vars)
    print('len model_pred_df', len(model_pred_df))
    model_pred_df = capitalize_column_names(model_pred_df)
    print('writing model_pred_df')
    model_pred_df.to_csv(os.environ.get('MODEL_PREDICTIONS_FILE'), index=False)

    model_pred_df['RANK_ROUND'] = model_pred_df['PRED_PROBABILITY'].apply(lambda x: round((x * 10)))
    zero_ndx = model_pred_df['RANK_ROUND'] == 0
    model_pred_df.loc[zero_ndx, 'RANK_ROUND'] = 1

    print('Lenght of model_pred_df: {}'.format(len(model_pred_df)))
    get_prob_info(model_pred_df['PRED_PROBABILITY'])
    get_pred_info(model_pred_df['PRED_CLASS'])

    ppd_dpc_output_file = ppd_score_out_dir + 'Polo_Addr_Rank_Scored_PPD_DPC_Pop.csv'
    print('\tsaving predictions to {}'.format(ppd_score_out_dir))
    model_pred_df.to_csv(ppd_dpc_output_file, sep=',', header=True, index=True)

    archived_output_file = ppd_archive_dir + start_time_str + '_PPD_' + \
                           ppd_date_str + '_Polo_Addr_Rank_Scored_PPD_DPC_Pop.csv'
    model_pred_df.to_csv(archived_output_file, sep=',', header=True, index=True)

    model_input_file = ppd_archive_dir + start_time_str + '_PPD_' + ppd_date_str + '_Polo_Addr_Rank_Input_Data.csv'
    model_data_pruned.to_csv(model_input_file, sep=',', header=True, index=True)


def get_input_data():
    ppd_data, ppd_date = get_ppd_data_and_date()

    entity_data = get_entity_data()

    if len(entity_data.ent_comm_at) == 0:
        raise InvalidDataException('No ent_comm_at entity data was loaded.')

    if len(entity_data.ent_comm_usg) == 0:
        raise InvalidDataException('No ent_comm_usg entity data was loaded.')

    return InputData(
        ppd=ppd_data,
        data=ppd+date,
        entity_data
    )


def get_model_data():
    model_file = os.environ.get('MODEL_FILE')
    model_var_file = os.environ.get('MODEL_VAR_FILE')

    print('-- Loading Model and Variables --')

    return ModelData(
        model=pickle.load(open(model_file, 'rb')),
        variables=pickle.load(open(model_var_file, 'rb'))
    )


def get_ppd_data_and_date():
    ppd_file = os.environ.get('PPD_FILE')
    require_latest_ppd_data = True if os.environ.get('REQUIRE_LATEST_PPD_DATA').lower()=='true' else False
    ppd_data = None
    ppd_date = None

    LOGGER.info('--- Loading PPD Data ---')

    if require_latest_ppd_data:
        ppd_data, ppd_date = get_latest_ppd_data_and_date()
    else:
        ppd_data, ppd_date = extract_ppd_data_and_date_from_file(ppd_file)

    return ppd_data, ppd_date


def get_entity_data():
    LOGGER.info('--- Loading Entity Data ---')

    return EntityData(
        entity_comm_at=extract_entity_data_from_file(os.environ.get('ENTITY_COMM_AT_FILE')),
        entity_comm_usg=extract_entity_data_from_file(os.environ.get('ENTITY_COMM_USG_FILE')),
        post_addr_at=extract_entity_data_from_file(os.environ.get('POST_ADDR_AT_FILE')),
        license_lt=extract_entity_data_from_file(os.environ.get('LICENSE_LT_FILE')),
        entity_key_et=extract_entity_data_from_file(os.environ.get('ENTITY_KEY_ET_FILE')),
    )


def get_latest_ppd_data_and_date():
    ppd_data, ppd_timestamp = get_latest_ppd_data()

    ppd_date = convert_timestamp_to_datetime(ppd_timestamp)

    return ppd_data, ppd_date


def extract_ppd_data_and_date_from_file(ppd_file):
    ppd_data = pd.read_csv(ppd_file, dtype=str)

    ppd_timestamp = extract_ppd_date_from_filename(ppd_file)

    ppd_date = convert_timestamp_to_datetime(ppd_timestamp)


def extract_entity_data_from_file(filename):
    return pd.read_csv(filename, dtype=str, na_values=['', '(null)'])


def extract_ppd_date_from_filename(ppd_file):
    """ Extract the timestamp from a PPD data file path of the form '.../ppd_data_YYYYMMDD.csv'. """
    ppd_filename = Path(ppd_file).name

    match = re.match(r'ppd_data_([0-9]+)\.csv', path.name)

    return match.group(1)


def convert_timestamp_to_datetime(ppd_timestamp):
    return datetime.datetime.strptime(ppd_timestamp, '%Y%m%d')


if __name__ == '__main__':
    main()