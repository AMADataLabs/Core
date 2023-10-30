import pandas as pd
import datetime
import logging
import os
import settings
import connection

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def get_practice_data():
    AMAEDW = connection.edw_connect()
    party_ids = pd.read_sql(con=AMAEDW, sql=(os.environ.get('ME_QUERY')))
    med_prof = pd.read_sql(con=AMAEDW, sql=(os.environ.get('MED_QUERY')))
    mpa = pd.read_sql(con=AMAEDW, sql=(os.environ.get('MPA_QUERY')))
    spec = pd.read_sql(con=AMAEDW, sql=(os.environ.get('SPEC_QUERY')))
    award = pd.read_sql(con=AMAEDW, sql=(os.environ.get('AWARD_QUERY')))
    practice_data = [party_ids, med_prof, mpa, spec, award]
    return practice_data

def transform_practice_data(practice_data, ov_me):
    practice_data[4].EXPIRATION_DT = pd.to_datetime(practice_data[4].EXPIRATION_DT)
    ov_universe = pd.merge(practice_data[0], ov_me, left_on='ME', right_on='medical_education_number')
    awards = practice_data[4][practice_data[4].EXPIRATION_DT>datetime.datetime.today()].sort_values('EXPIRATION_DT').drop_duplicates('PARTY_ID', keep='last')
    all_practice_data = pd.merge(ov_universe, practice_data[1], on='PARTY_ID', how='left')
    all_practice_data = pd.merge(all_practice_data, practice_data[3][practice_data[3].PREFE_LVL==1], on='PARTY_ID', how='left')
    all_practice_data = pd.merge(all_practice_data, practice_data[3][practice_data[3].PREFE_LVL==2], on='PARTY_ID', suffixes = ['_PRIM','_SEC'], how='left')
    all_practice_data = pd.merge(all_practice_data, practice_data[2], on=['TOP_ID','EMPLOYER_ID'], how='left')
    all_practice_data = pd.merge(all_practice_data, awards, on='PARTY_ID', how='left')
    return all_practice_data

def load(data):
    out_folder = os.environ.get('LOCAL_OUT')
    filename = f'{out_folder}/Practice_Data_{str(datetime.date.today())}.csv'
    data.to_csv(filename, index = False)
    return filename

def practice():
    LOGGER.info('Loading MEs from OneView...')
    ov_me = connection.get_oneview_me()
    LOGGER.info('Loading practice data from EDW...')
    practice_data = get_practice_data()
    LOGGER.info('Transforming practice data...')
    all_practice = transform_practice_data(practice_data, ov_me)
    filename = load(all_practice)
    LOGGER.info(f'Data saved at {filename}')

if __name__ == "__main__":
    practice()