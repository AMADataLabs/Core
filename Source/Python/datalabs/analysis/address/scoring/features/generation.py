""" Main module for adding all relevant features to a base dataset """
# pylint: disable=line-too-long, pointless-string-statement
"""
    This script is intended for running locally to create the features on Humach result data in order to
    create labeled training data for the address scoring model, but can also be used to create features on
    PPD population.

    note: address_key = f'{street_address}_{5_digit_zip}'

    Training data feature engineering:
        1. Extract and clean data:
            - ENTITY_COMM_AT_PROCESSED.txt      - entity_id|comm_id|begin_dt|end_dt|src_cat_code|comm_type|comm_cat
            - ENTITY_COMM_AT_USG_PROCESSED.txt  - entity_id|comm_id|comm_usage|usg_begin_dt|end_dt|src_cat_code
            - LICENSE_LT_PROCESSED.txt          - entity_id|comm_id|state_cd|lic_issue_dt|lic_exp_dt
            - POST_ADDR_AT_PROCESSED.txt        - comm_id|state_cd|address_key
            - HUMACH_PROCESSED.txt              - me|address_key|survey_date|comments|office_address_verified_updated|party_id|entity_id
            - triangulation_iqvia.txt           - me|address_key
            - triangulation_symphony.txt        - me|address_key
        2. Place the files inside datalabs/analysis/address/scoring/data/YYYY-MM-DD/* where YYYY-MM-DD is the as_of_date
        3. Use Humach survey result data to create a labeled dataset with the following target columns
            me|entity_id|comm_id|address_key|survey_date|comments|office_address_verified_updated|status

            Place this data inside datalabs/analysis/addres/scoring/training/YYYYMM/YYYY-MM-DD.txt
                * YYYYMM is the current year-month, and should match the YYYY-MM-DD from step 2
                * YYYY-MM-DD from "YYYY-MM-DD.txt" in this step however should be the date corresponding to the
                  survey month. For example, a survey sample generated at the end of May will be the June survey sample,
                  so the YYYY-MM-DD.txt for data from that sample would be called "2022-06-01.txt"
                  This filename is also used as the file's "as_of_date" for purposes of feaeture generation

            In summary, if I extract data from AIMS and the other sources on Aug 16 2022 and I'm building a dataset
            with survey results from the June Humach sample, I would have the following:

                - datalabs/analysis/addres/scoring/data/2022-08-16/<all files from step 1>
                - datalabs/analysis/addres/scoring/training/202208/2022-06-01.txt           (Humach result file step 3)

            To create feature data for the survey results from the June sample, I would run:
                - python generation.py 2022-08-16 TRAIN_202208 2022-06-01

    Instructions:
        1.
"""
# pylint: disable=import-error, redefined-builtin, unused-import, wrong-import-position
import logging
import os
from string import ascii_letters, digits
import sys
import pickle as pk
from datalabs.analysis.address.scoring.common import load_processed_data, get_active_polo_eligible_addresses, log_info, keep_alphanumeric, clean_zip
from datalabs.analysis.address.scoring.features import license, entity_comm, entity_comm_usg, humach
from datalabs.analysis.address.scoring.features.triangulation import triangulation


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

# INPUT_PATH = f"../data/{AS_OF_DATE}"

IS_TRAINING = 'TRAIN' in RUN_TYPE.upper()
if IS_TRAINING:
    yyyymm = RUN_TYPE.split('_')[1]
    print(f'TRAINING MODE - USING DATA IN /training/{yyyymm}')
    INPUT_PATH = f"../data/{DATA_FOLDER}"
    FILE_BASE_DATA = f"../training/{yyyymm}/{AS_OF_DATE}.txt"
    SAVE_DIR = f"../training/{yyyymm}/features/"
else:
    INPUT_PATH = f"../data/{AS_OF_DATE}"
    FILE_BASE_DATA = f"{INPUT_PATH}/BASE_DATA.txt"
    SAVE_DIR = f"../data/{AS_OF_DATE}/features/"

if not os.path.exists(SAVE_DIR):
    os.mkdir(SAVE_DIR)

FILE_POST_ADDR_AT = f"{INPUT_PATH}/POST_ADDR_AT_PROCESSED.txt"
FILE_ENTITY_COMM_AT = f"{INPUT_PATH}/ENTITY_COMM_AT_PROCESSED.txt"
FILE_ENTITY_COMM_USG_AT = f"{INPUT_PATH}/ENTITY_COMM_USG_AT_PROCESSED.txt"
FILE_LICENSE_LT = f"{INPUT_PATH}/LICENSE_LT_PROCESSED.txt"
FILE_HUMACH = f"{INPUT_PATH}/HUMACH_PROCESSED.txt"
FILE_IQVIA = f"{INPUT_PATH}/triangulation_iqvia.txt"
FILE_SYMPHONY = f"{INPUT_PATH}/triangulation_symphony.txt"


if __name__ == '__main__':
    log_info('RUN_TYPE:', RUN_TYPE)
    log_info('LOADING BASE_DATA')
    BASE_DATA = load_processed_data(FILE_BASE_DATA)
    BASE_DATA['ADDRESS_KEY'] = BASE_DATA['ADDRESS_KEY'].fillna('').astype(str).apply(str.strip).apply(str.upper).apply(keep_alphanumeric).apply(clean_zip)
    # if 'TRAIN' not in RUN_TYPE.upper():
    #     log_info('RUN_TYPE is NOT set to TRAINING mode --- fetching active POLO-eligible addresses for base population')
    #     BASE_DATA = get_active_polo_eligible_addresses(BASE_DATA, FILE_ENTITY_COMM_AT, FILE_POST_ADDR_AT, AS_OF_DATE)
    #     with open('base_data.pk', 'wb') as f:
    #         log_info('SAVING BASE_DATA')
    #     pk.dump(BASE_DATA, f)
    # else:
    #     with open('base_data.pk', 'rb') as f:
    #         log_info('READING SAVED BASE_DATA')
    #         BASE_DATA = pk.load(f)

    log_info('BASE_DATA MEMORY:', BASE_DATA.memory_usage().sum() / 1024 ** 2)

    print(BASE_DATA.shape[0])

    # for speedy runs in testing / debugging
    # print('sampling 10%')
    # BASE_DATA = BASE_DATA.sample(round(BASE_DATA.shape[0] / 10))
    # print(BASE_DATA.shape[0])

    log_info('ADD ENTITY_COMM FEATURES')
    entity_comm.add_entity_comm_at_features(BASE_DATA, FILE_ENTITY_COMM_AT, AS_OF_DATE, SAVE_DIR)
    log_info('ADD ENTITY_COMM_USG FEATURES')
    entity_comm_usg.add_entity_comm_usg_at_features(BASE_DATA, FILE_ENTITY_COMM_USG_AT, AS_OF_DATE, SAVE_DIR)
    log_info('ADD LICENSE FEATURES')
    license.add_license_features(BASE_DATA, FILE_LICENSE_LT, FILE_POST_ADDR_AT, AS_OF_DATE, SAVE_DIR)
    log_info('ADD HUMACH FEATURES')
    humach.add_humach_features(BASE_DATA, FILE_HUMACH, AS_OF_DATE, SAVE_DIR, IS_TRAINING)
    log_info('ADD TRIANGULATION')
    iqvia = triangulation.TriangulationDataSource(FILE_IQVIA, 'IQVIA')
    symphony = triangulation.TriangulationDataSource(FILE_SYMPHONY, 'SYMPHONY')
    log_info('ADD TRIANGULATION - IQVIA')
    triangulation.add_triangulation_features(BASE_DATA, iqvia, AS_OF_DATE, SAVE_DIR)
    log_info('ADD TRIANGULATION - SYMPHONY')
    triangulation.add_triangulation_features(BASE_DATA, symphony, AS_OF_DATE, SAVE_DIR)
