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
    return ethnicity

def get_reference():
    oneview_dir = os.environ.get('ONEVIEW_FOLDER')
    reference_filename = use.get_newest(oneview_dir, 'AIMS_ETHNICITY_ER')
    reference = pd.read_csv(reference_filename, sep='|')
    return reference

def ethnicity_extract():
    me_to_entity = get_me_entity()
    ethnicity = get_person_ethnicity()
    reference = get_reference()
    tables = [me_to_entity, ethnicity, reference]
    return tables

#transform
def find_multiple_identities(ethnicity):
    single_identity = ethnicity.drop_duplicates(['entity_id', 'ethnicity_id'], keep=False)
    multiple_identities = ethnicity[(ethnicity.entity_id.isin(single_identity.entity_id))==False].drop_duplicates('entity_id')
    multiple_identities['race_ethnicity'] = 'Mixed Race/Ethnicity'
    return single_identity, multiple_identities[['entity_id','race_ethnicity']]
    
def add_reference(single_identity, reference):
    single_reference = pd.merge(single_identity, reference, left_on='ethnicity_id', right_on='ethnicity')
    single_reference['race_ethnicity'] = single_reference.parent_category_desc
    return single_reference[['entity_id','race_ethnicity']]

def fix_me_2(me_number):
    me_number = me_number[1:].strip()
    return me_number

def ethnicity_transform(tables):
    me_to_entity = tables[0]
    me_to_entity['medical_education_number'] = use.fix_me(me_to_entity.ME)
    single_identity, multi_identity = find_multiple_identities(tables[1])
    single_identity = add_reference(single_identity, tables[2])
    race_ethnicity = pd.concat([single_identity, multi_identity])
    race_ethnicity['ENTITY_ID'] = race_ethnicity.entity_id.astype(str)
    race_ethnicity = pd.merge(race_ethnicity, me_to_entity, on='ENTITY_ID')
    race_ethnicity['medical_education_number'] = [fix_me_2(x) for x in race_ethnicity.medical_education_number]
    race_ethnicity = race_ethnicity[['medical_education_number','race_ethnicity']]
    return race_ethnicity

#load
def ethnicity_load(race_ethnicity):
    oneview_dir = os.environ.get('ONEVIEW_FOLDER')
    today = str(date.today())
    # race_ethnicity.to_csv(f'{oneview_dir}PhysicianRaceEthnicity_{today}.csv', sep='|', index=False)
    race_ethnicity.head(10).to_csv(f'C:/Users/vigrose/DataPhysicianRaceEthnicity_{today}.csv', sep='|', index=False)
    race_ethnicity.head(10).to_csv(f'C:/Users/vigrose/DataPhysicianRaceEthnicity_2_{today}.csv', index=False)

def race_ethnicity_etl():
    LOGGER.info('Extract...')
    tables = ethnicity_extract()
    LOGGER.info('Transform...')
    race_ethnicity = ethnicity_transform(tables)
    LOGGER.info('Load...')
    ethnicity_load(race_ethnicity)

if __name__ == "__main__":
    race_ethnicity_etl()