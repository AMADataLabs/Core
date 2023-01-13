import os
from datetime import datetime, date
import pandas as pd
import settings
from datalabs.access.edw import EDW
import logging
import pyodbc
import useful_functions as use

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

#extract
def aims_connect():
    username = os.environ.get('CREDENTIALS_AIMS_USERNAME')
    password_aims = os.environ.get('CREDENTIALS_AIMS_PASSWORD')
    s = "DSN=aims_prod; UID={}; PWD={}".format(username, password_aims)
    informix = pyodbc.connect(s)
    return informix

def get_me_entity():
    me_entity_query = os.environ.get('ME_ENTITY_QUERY')
    with EDW() as edw:
        LOGGER.info('Getting ME numbers...')
        me_to_entity = edw.read(me_entity_query)
    return me_to_entity

def get_person_ethnicity():
    oneview_dir = os.environ.get('ONEVIEW_FOLDER')
    ethnicity_filename = use.get_newest(oneview_dir, 'AIMS_PERSON_ETHNICITY_ET')
    ethnicity = pd.read_csv(ethnicity_filename, sep='|')
    ethnicity = ethnicity[(ethnicity.active_ind=='Y')&(ethnicity.preferred_ind=='Y')]
    return ethnicity

def get_reference():
    oneview_dir = os.environ.get('ONEVIEW_FOLDER')
    reference_filename = use.get_newest(oneview_dir, 'AIMS_ETHNICITY_ER')
    reference = pd.read_csv(reference_filename)
    reference.parent_category_desc = [x.strip() for x in reference.parent_category_desc]
    return reference

def ethnicity_extract():
    me_to_entity = get_me_entity()
    ethnicity = get_person_ethnicity()
    reference = get_reference()
    tables = [me_to_entity, ethnicity, reference]
    return tables

#transform
def find_multiple_identities(ethnicity):
    ethnicity = ethnicity.drop_duplicates(['entity_id', 'parent_category_desc'])
    LOGGER.info(f'Ethnicity table is {len(ethnicity)}')
    single_identity = ethnicity.drop_duplicates('entity_id', keep=False)
    LOGGER.info(f'Single identity is {len(single_identity)}')
    additional = ethnicity[(~ethnicity.entity_id.isin(single_identity.entity_id))&(ethnicity.parent_category_desc!='Unknown')].drop_duplicates('entity_id', keep=False)
    LOGGER.info(f'Additional single identity is {len(additional)}')
    single_identity = pd.concat([single_identity, additional])
    LOGGER.info(f'Combined single identity is {len(single_identity)}')
    multiple_identities = ethnicity[~ethnicity.entity_id.isin(single_identity.entity_id)].drop_duplicates('entity_id')
    multiple_identities['race_ethnicity'] = 'Mixed Race/Ethnicity'
    single_identity['race_ethnicity'] = single_identity.parent_category_desc
    single_identity = single_identity.drop_duplicates('entity_id')
    LOGGER.info(f'Single identity is {len(single_identity)}')
    LOGGER.info(f'Multiple identity is {len(multiple_identities)}')
    return single_identity[['entity_id','race_ethnicity']], multiple_identities[['entity_id','race_ethnicity']]
    
def add_reference(ethnicity, reference):
    ethnicity['ethnicity'] = ethnicity.ethnicity_id.astype(str)
    ethnicity_reference = pd.merge(ethnicity, reference, on='ethnicity')
    return ethnicity_reference

def ethnicity_transform(tables):
    me_to_entity = tables[0]
    LOGGER.info(f'Me Entity table is {len(me_to_entity)}')
    me_to_entity['medical_education_number'] = [use.fix_me(x) for x in me_to_entity.ME]
    
    ethnicity = add_reference(tables[1], tables[2])
    single_identity, multi_identity = find_multiple_identities(ethnicity)
    race_ethnicity_table = pd.concat([single_identity, multi_identity])
    race_ethnicity_table['ENTITY_ID'] = race_ethnicity_table.entity_id.astype(str)
    race_ethnicity_table = pd.merge(race_ethnicity_table, me_to_entity, on='ENTITY_ID')
    race_ethnicity_table = race_ethnicity_table[['medical_education_number','race_ethnicity']]
    LOGGER.info(f'Race Ethnicity table is {len(race_ethnicity_table)}')
    return race_ethnicity_table

# def quality_check(new):
#     oneview_dir = os.environ.get('ONEVIEW_FOLDER')
#     old = pd.read_csv(f'{oneview_dir}PhysicianRaceEthnicity-ETL.psv', sep='|')
#     len(new[~new.medical_education_number.isin(old.medical_education_number)])

#load
def ethnicity_load(race_ethnicity_table):
    oneview_dir = os.environ.get('ONEVIEW_FOLDER')
    today = str(date.today())
    race_ethnicity_table.to_csv(f'{oneview_dir}PhysicianRaceEthnicity-ETL.psv', sep='|', index=False)
    race_ethnicity_table.to_csv(f'C:/Users/vigrose/Data/MasterfileCore/PhysicianRaceEthnicity_{today}.psv', sep='|', index=False)
    race_ethnicity_table.to_csv(f'C:/Users/vigrose/Data/MasterfileCore/PhysicianRaceEthnicity_2_{today}.csv', index=False)

def race_ethnicity_etl():
    LOGGER.info('Extract...')
    tables = ethnicity_extract()
    LOGGER.info('Transform...')
    race_ethnicity_table = ethnicity_transform(tables)
    LOGGER.info('Load...')
    ethnicity_load(race_ethnicity_table)

if __name__ == "__main__":
    race_ethnicity_etl()