""" Main module for adding all relevant features to a base dataset """
# pylint: disable=import-error, redefined-builtin
import logging
import os
import sys
import pickle as pk
from datalabs.analysis.address.scoring.common import load_processed_data, get_active_polo_eligible_addresses, log_info
from datalabs.analysis.address.scoring.features import license, entity_comm, entity_comm_usg


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

DATA_FOLDER = sys.argv[1]

# if 'TRAIN' then we don't need to fetch POLO-eligible addresses because BASE_DATA will already contain
# the addresses we want to make features for (will contain ENTITY_ID + COMM_ID + VERIFIED)
RUN_TYPE = sys.argv[2]

if len(sys.argv) > 3:
    AS_OF_DATE = sys.argv[3]
else:
    AS_OF_DATE = DATA_FOLDER

INPUT_PATH = f"../data/{AS_OF_DATE}"
SAVE_DIR = f"../data/{AS_OF_DATE}/features/"
if not os.path.exists(SAVE_DIR):
    os.mkdir(SAVE_DIR)

FILE_BASE_DATA = f"{INPUT_PATH}/BASE_DATA.txt"
FILE_POST_ADDR_AT = f"{INPUT_PATH}/POST_ADDR_AT_PROCESSED.txt"
FILE_ENTITY_COMM_AT = f"{INPUT_PATH}/ENTITY_COMM_AT_PROCESSED.txt"
FILE_ENTITY_COMM_USG_AT = f"{INPUT_PATH}/ENTITY_COMM_USG_AT_PROCESSED.txt"
FILE_LICENSE_LT = f"{INPUT_PATH}/LICENSE_LT_PROCESSED.txt"


if __name__ == '__main__':
    log_info('RUN_TYPE:', RUN_TYPE)
    log_info('LOADING BASE_DATA')
    BASE_DATA = load_processed_data(FILE_BASE_DATA)
    if 'TRAIN' not in RUN_TYPE.upper():
        log_info('RUN_TYPE is NOT set to TRAINING mode --- fetching active POLO-eligible addresses for base population')
        BASE_DATA = get_active_polo_eligible_addresses(BASE_DATA, FILE_ENTITY_COMM_AT, FILE_POST_ADDR_AT, AS_OF_DATE)
        with open('base_data.pk', 'wb') as f:
            log_info('SAVING BASE_DATA')
            pk.dump(BASE_DATA, f)
    else:
        with open('base_data.pk', 'rb') as f:
            log_info('READING SAVED BASE_DATA')
            BASE_DATA = pk.load(f)

    log_info('BASE_DATA MEMORY:', BASE_DATA.memory_usage().sum() / 1024 ** 2)

    print(BASE_DATA.shape[0])
    # print('sampling 50%')
    # BASE_DATA = BASE_DATA.sample(round(BASE_DATA.shape[0] / 2))
    # print(BASE_DATA.shape[0])

    log_info('ADD ENTITY_COMM FEATURES')
    entity_comm.add_entity_comm_at_features(BASE_DATA, FILE_ENTITY_COMM_AT, AS_OF_DATE, SAVE_DIR)
    log_info('ADD ENTITY_COMM_USG FEATURES')
    entity_comm_usg.add_entity_comm_usg_at_features(BASE_DATA, FILE_ENTITY_COMM_USG_AT, AS_OF_DATE, SAVE_DIR)
    log_info('ADD LICENSE FEATURES')
    license.add_license_features(BASE_DATA, FILE_LICENSE_LT, FILE_POST_ADDR_AT, AS_OF_DATE, SAVE_DIR)
