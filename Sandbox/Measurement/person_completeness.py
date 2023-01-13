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

def get_race_ethnicity():
    folder = os.environ.get('FOLDER')
    race_file = use.get_newest(folder, 'PhysicianRaceEthnicity')
    race = pd.read_csv(race_file)
    race.medical_education_number = use.fix_me(race.medical_education_number)
    return race

def get_person_data():
    with EDW() as edw:
        party_ids = edw.read(os.environ.get('PARTY_ID_QUERY'))
        entity_ids = edw.read(os.environ.get('ENTITY_ID_QUERY'))
        names = edw.read(os.environ.get('NAME_QUERY'))
        persons = edw.read(os.environ.get('PERSON_QUERY'))
    person_data = [party_ids, entity_ids, names, persons]
    return person_data

def transform_person_data(person_data, ov_me, race):
    ids = pd.merge(person_data[1], person_data[0], on='PARTY_ID')
    universe = pd.merge(ids, ov_me, left_on='ME', right_on='medical_education_number', how='right')
    all_person_data= pd.merge(universe, person_data[2], on='PARTY_ID',how='left').drop_duplicates()
    all_person_data= pd.merge(all_person_data, race, on='medical_education_number', how='left')
    all_person_data = pd.merge(all_person_data, person_data[3], on='PARTY_ID',how='left').drop_duplicates()
    return all_person_data

def measure_person(all_person_data):
    today = datetime.date.today()
    types = ['Physician','Student','Resident']
    dead_mes = list(all_person_data[(all_person_data.MORTALITY_STS_CD=='C')].ME)
    all_mes = list(all_person_data.ME)
    us_mes = list(all_person_data[(all_person_data.BIRTH_COUNTRY_ID==6705)].ME)
    elements = [
        {'data_element': 'Party ID',
        'element':'PARTY_ID',
        'null': '',
        'universe': all_mes},
        {'data_element': 'Entity ID',
        'element':'ENTITY_ID',
        'null': '',
        'universe': all_mes},
        {'data_element': 'First Name',
        'element':'FIRST_NM',
        'null': '',
        'universe': all_mes},
        {'data_element': 'Middle Name',
        'element':'MIDDLE_NM',
        'null': '',
        'universe': all_mes},
        {'data_element': 'Last Name',
        'element':'LAST_NM',
        'null': '',
        'universe': all_mes},
        {'data_element': 'Name Suffix',
        'element':'SUFFIX',
        'null': '',
        'universe': all_mes},
        {'data_element': 'Label Name',
        'element':'LABEL_NM',
        'null': '',
        'universe': all_mes},
        {'data_element': 'Name Type',
        'element':'NM_TYPE',
        'null': '',
        'universe': all_mes},
        {'data_element': 'Person Type',
        'element':'type',
        'null': '',
        'universe': all_mes},
        {'data_element': 'Race/Ethnicity',
        'element':'race_ethnicity',
        'null': 'Unknown',
        'universe': all_mes},
        {'data_element': 'Birth Date',
        'element':'BIRTH_DT',
        'null': datetime.date(1900, 1, 1),
        'universe':all_mes},
        {'data_element': 'Birth City',
        'element':'BIRTH_CITY_NM',
        'null': '',
        'universe': all_mes},
        {'data_element': 'Birth State',
        'element':'BIRTH_STATE_ID',
        'null': '',
        'universe': us_mes},
        {'data_element': 'Birth Country',
        'element':'BIRTH_COUNTRY_ID',
        'null': '',
        'universe': all_mes},
        {'data_element': 'Gender',
        'element':'GENDER_CD',
        'null': '',
        'universe':all_mes},
        {'data_element': 'Death Date',
        'element':'DEATH_DT',
        'null': '',
        'universe':dead_mes},     
    ]
    dict_list = []
    for typo in types:
        for element in elements:
            universe = len(all_person_data[(all_person_data.type==typo)&(all_person_data.ME.isin(element['universe']))])
            complete = len(all_person_data[(all_person_data.type==typo)&~(all_person_data[element['element']].isna())&(all_person_data.ME.isin(element['universe']))])
            true_complete = len(all_person_data[(all_person_data.type==typo)&(all_person_data[element['element']]!=element['null'])&~(all_person_data[element['element']].isna())&(all_person_data.ME.isin(element['universe']))])
            new_dict = {
                'Universe': typo,
                'Data Element': element['data_element'],
                'Complete': complete,
                'Complete and Known': true_complete,
                'Universe Total': universe,
                'Date': today,
                'Measure':'Completeness'
            }
            dict_list.append(new_dict)
    return dict_list

def load(dict_list):
    out_folder = os.environ.get('LOCAL_OUT')
    pd.DataFrame(dict_list).to_csv(f'{out_folder}/Person_Completeness_{str(datetime.date.today())}.csv', index=False)

def get_person_completeness():
    LOGGER.info('Loading MEs from OneView...')
    ov_me = measurement.get_oneview_me()
    LOGGER.info('Loading race ethnicity data...')
    race_ethnicity = get_race_ethnicity()
    LOGGER.info('Loading person data from EDW...')
    person_data = get_person_data()
    LOGGER.info('Transforming person data...')
    all_person= transform_person_data(person_data, ov_me, race_ethnicity)
    LOGGER.info('Calculating person data completeness...')
    dict_list = measure_person(all_person)
    LOGGER.info('Loading results...')
    load(dict_list)

if __name__ == "__main__":
    get_person_completeness()