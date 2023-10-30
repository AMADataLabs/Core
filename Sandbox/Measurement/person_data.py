import pandas as pd
import datetime
import logging
import os
import settings
import connection

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def get_race_ethnicity():
    folder = os.environ.get('FOLDER')
    race_file = connection.get_newest(folder, 'PhysicianRaceEthnicity')
    race = pd.read_csv(race_file)
    race.medical_education_number = connection.fix_me(race.medical_education_number)
    return race

def get_person_data():
    AMAEDW = connection.edw_connect()
    party_ids = pd.read_sql(con=AMAEDW, sql=(os.environ.get('PARTY_ID_QUERY')))
    entity_ids = pd.read_sql(con=AMAEDW, sql=(os.environ.get('ENTITY_ID_QUERY')))
    names = pd.read_sql(con=AMAEDW, sql=(os.environ.get('NAME_QUERY')))
    persons = pd.read_sql(con=AMAEDW, sql=(os.environ.get('PERSON_QUERY')))
    person_data = [party_ids, entity_ids, names, persons]
    return person_data

def transform_person_data(person_data, ov_me, race):
    ids = pd.merge(person_data[1], person_data[0], on='PARTY_ID')
    universe = pd.merge(ids, ov_me, left_on='ME', right_on='medical_education_number', how='right')
    all_person_data= pd.merge(universe, person_data[2], on='PARTY_ID',how='left').drop_duplicates()
    all_person_data= pd.merge(all_person_data, race, on='medical_education_number', how='left')
    all_person_data = pd.merge(all_person_data, person_data[3], on='PARTY_ID',how='left').drop_duplicates()
    return all_person_data

def load(data):
    out_folder = os.environ.get('LOCAL_OUT')
    filename = f'{out_folder}/Person_Data_{str(datetime.date.today())}.csv'
    data.to_csv(filename, index=False)
    return filename

def person():
    LOGGER.info('Loading MEs from OneView...')
    ov_me = connection.get_oneview_me()
    LOGGER.info('Loading race ethnicity data...')
    race_ethnicity = get_race_ethnicity()
    LOGGER.info('Loading person data from EDW...')
    person_data = get_person_data()
    LOGGER.info('Transforming person data...')
    all_person= transform_person_data(person_data, ov_me, race_ethnicity)
    LOGGER.info('Loading results...')
    filename = load(all_person)
    LOGGER.info(f'Data saved at {filename}')

if __name__ == "__main__":
    person()