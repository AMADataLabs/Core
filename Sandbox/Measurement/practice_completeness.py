import pandas as pd
import datetime
import logging
import os
import settings
import useful_functions as use
import measurement
from datalabs.access.edw import EDW

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def get_practice_data():
    with EDW() as edw:
        party_ids = edw.read(os.environ.get('ME_QUERY'))
        med_prof = edw.read(os.environ.get('MED_QUERY'))
        mpa = edw.read(os.environ.get('MPA_QUERY'))
        spec = edw.read(os.environ.get('SPEC_QUERY'))
        award = edw.read(os.environ.get('AWARD_QUERY'))
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

def measure_practice(all_practice_data):
    today = datetime.date.today()
    types = ['Physician','Student','Resident']
    elements = [
        {'data_element': 'TOP',
        'element':'TOP_ID',
        'null': 115.0},
        {'data_element': 'PE',
        'element':'EMPLOYER_ID',
        'null': 391.0},
        {'data_element': 'MPA',
        'element':'MPA_CD',
        'null': 'NCL'},
        {'data_element': 'Primary Specialty',
        'element':'SPEC_CD_PRIM',
        'null': 'US '},
        {'data_element': 'Secondary Specialty',
        'element':'SPEC_CD_SEC',
        'null': 'US '},
        {'data_element': 'PRA Award Flag',
        'element':'EXPIRATION_DT',
        'null': ''}
    ]
    dict_list = []
    for typo in types:
        total = len(all_practice_data[all_practice_data.type==typo])
        for element in elements:
            complete = len(all_practice_data[(all_practice_data.type==typo)&~(all_practice_data[element['element']].isna())])
            true_complete = len(all_practice_data[(all_practice_data.type==typo)&(all_practice_data[element['element']]!=element['null'])&~(all_practice_data[element['element']].isna())])
            new_dict = {
                'Universe': typo,
                'Data Element': element['data_element'],
                'Complete': complete,
                'Complete and Known': true_complete,
                'Universe Total': total,
                'Date': today,
                'Measure':'Completeness'
            }
            dict_list.append(new_dict)
    return dict_list

def load(dict_list):
    out_folder = os.environ.get('LOCAL_OUT')
    pd.DataFrame(dict_list).to_csv(f'{out_folder}/Practice_Completeness_{str(datetime.date.today())}.csv', index=False)

def get_practice_completeness():
    LOGGER.info('Loading MEs from OneView...')
    ov_me = measurement.get_oneview_me()
    LOGGER.info('Loading practice data from EDW...')
    practice_data = get_practice_data()
    LOGGER.info('Transforming practice data...')
    all_practice = transform_practice_data(practice_data, ov_me)
    LOGGER.info('Calculating practice data completeness...')
    dict_list = measure_practice(all_practice)
    LOGGER.info('Loading results...')
    load(dict_list)

if __name__ == "__main__":
    get_practice_completeness()