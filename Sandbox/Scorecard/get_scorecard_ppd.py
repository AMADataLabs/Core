import os
from datetime import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta
import settings
import logging

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def get_columns():
    cols = [
        'ME',
        'RECORD_ID',
        'UPDATE_TYPE',
        'ADDRESS_TYPE',
        'MAILING_NAME',
        'LAST_NAME',
        'FIRST_NAME',
        'MIDDLE_NAME',
        'SUFFIX',
        'MAILING_LINE_1',
        'MAILING_LINE_2',
        'CITY',
        'STATE',
        'ZIP',
        'SECTOR',
        'CARRIER_ROUTE',
        'ADDRESS_UNDELIVERABLE_FLAG',
        'FIPS_COUNTY',
        'FIPS_STATE',
        'PRINTER_CONTROL_CODE',
        'PC_ZIP',
        'PC_SECTOR',
        'DELIVERY_POINT_CODE',
        'CHECK_DIGIT',
        'PRINTER_CONTROL_CODE_2',
        'REGION',
        'DIVISION',
        'GROUP',
        'TRACT',
        'SUFFIX_CENSUS',
        'BLOCK_GROUP',
        'MSA_POPULATION_SIZE',
        'MICRO_METRO_IND',
        'CBSA',
        'CBSA_DIV_IND',
        'MD_DO_CODE',
        'BIRTH_YEAR',
        'BIRTH_CITY',
        'BIRTH_STATE',
        'BIRTH_COUNTRY',
        'GENDER',
        'TELEPHONE_NUMBER',
        'PRESUMED_DEAD_FLAG',
        'FAX_NUMBER',
        'TOP_CD',
        'PE_CD',
        'PRIM_SPEC_CD',
        'SEC_SPEC_CD',
        'MPA_CD',
        'PRA_RECIPIENT',
        'PRA_EXP_DT',
        'GME_CONF_FLG',
        'FROM_DT',
        'TO_DT',
        'YEAR_IN_PROGRAM',
        'POST_GRADUATE_YEAR',
        'GME_SPEC_1',
        'GME_SPEC_2',
        'TRAINING_TYPE',
        'GME_INST_STATE',
        'GME_INST_ID',
        'MEDSCHOOL_STATE',
        'MEDSCHOOL_ID',
        'MEDSCHOOL_GRAD_YEAR',
        'NO_CONTACT_IND',
        'NO_WEB_FLAG',
        'PDRP_FLAG',
        'PDRP_START_DT',
        'POLO_MAILING_LINE_1',
        'POLO_MAILING_LINE_2',
        'POLO_CITY',
        'POLO_STATE',
        'POLO_ZIP',
        'POLO_SECTOR',
        'POLO_CARRIER_ROUTE',
        'MOST_RECENT_FORMER_LAST_NAME',
        'MOST_RECENT_FORMER_MIDDLE_NAME',
        'MOST_RECENT_FORMER_FIRST_NAME',
        'NEXT_MOST_RECENT_FORMER_LAST',
        'NEXT_MOST_RECENT_FORMER_MIDDLE',
        'NEXT_MOST_RECENT_FORMER_FIRST'
    ]
    return cols


def get_ppd_date():
    today = datetime.today()
    last_month = (today - relativedelta(months=1))
    last_day = (last_month + relativedelta(day=31))
    last_day.weekday()
    if last_day.weekday()==5:
        ppd_date = last_day
    else:
        ppd_date = (last_day + relativedelta(days=7))
        possibilities = pd.date_range(last_day, today)
        for day in possibilities:
            if day.weekday()==5:
                ppd_date = day
                break
    ppd_date = ppd_date.strftime("%Y%m%d")
    return ppd_date

def create_ppd_csv():
    ppd_folder = os.environ.get('PPD_DIR')
    scorecard_folder = os.environ.get('LOCAL')
    ppd_date = get_ppd_date()
    ppd_filename = f'PhysicianProfessionalDataFile_{ppd_date}'
    LOGGER.info(f'Scorecard PPD is {ppd_filename}...')
    files = os.listdir(ppd_folder)
    ppd_path = [os.path.join(ppd_folder, basename) for basename in files if ppd_filename in basename][0]
    cols = get_columns()
    LOGGER.info('Getting PPD data from UDrive...')
    ppd = pd.read_csv(ppd_path, names=cols, sep='|', encoding='IBM437', index_col=False, dtype=object, engine='python')
    scorecard_ppd_file =  f'{scorecard_folder}/ppd_data_{ppd_date}.csv'
    LOGGER.info('Saving PPD as csv in scorecard folder...')
    ppd.to_csv(scorecard_ppd_file, header=True, index=False)
    return scorecard_ppd_file


