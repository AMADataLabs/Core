import pandas as pd
import psycopg2
import pyodbc
import datetime
import logging
import os
import settings
from datalabs.access.edw import EDW

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

#connect
def oneview_connect():
    conn = psycopg2.connect(
        host = os.environ.get('DATABASE_ONEVIEW_HOST'),
        database = os.environ.get('DATABASE_ONEVIEW_NAME'),
        user = os.environ.get('CREDENTIALS_ONEVIEW_USERNAME'),
        password = os.environ.get('CREDENTIALS_ONEVIEW_PASSWORD'))
    return conn

#read
def get_oneview_me(): 
    conn = oneview_connect()
    ov_me_sql = os.environ.get('ONEVIEW_ME')
    ov_me = pd.read_sql_query(ov_me_sql, conn)
    return ov_me

def get_education_data():
    with EDW() as edw:
        party_ids = edw.read(os.environ.get('ME_QUERY'))
        more_school_ids = edw.read(os.environ.get('MORE_SCHOOL_QUERY'))
        school_ids = edw.read(os.environ.get('SCHOOL_QUERY'))
        med_school = edw.read(os.environ.get('MED_SCHOOL_QUERY'))
        gme = edw.read(os.environ.get('GME_QUERY'))
        gme_year= edw.read(os.environ.get('YEAR_QUERY'))
        org_names = edw.read(os.environ.get('ORG_QUERY'))
    education_data = [party_ids, more_school_ids, school_ids, med_school, gme, gme_year, org_names]
    return education_data

#transform
def transform_org_names(org_names):
    org_names.THRU_DT = pd.to_datetime(org_names.THRU_DT)
    org_names = org_names.sort_values('THRU_DT').drop_duplicates('PARTY_HOSPITAL_ID', keep='last')
    return org_names

def transform_school_ids(education_data):
    school_ids = education_data[2].drop_duplicates()
    extra = education_data[1][~education_data[1].SCHOOL_ID.isin(school_ids.SCHOOL_ID)]
    school_ids = pd.concat([school_ids, extra])
    school_info = pd.merge(school_ids, education_data[6], left_on='PARTY_ID_SCHOOL', right_on='PARTY_HOSPITAL_ID', how='left').drop_duplicates()
    return school_info

def transform_gme(education_data):
    gme_singular = education_data[4].drop_duplicates('PARTY_ID')
    gme_with_info = pd.merge(gme_singular, education_data[6], on='PARTY_HOSPITAL_ID', how='left').drop_duplicates()
    return gme_with_info

def transform_med_school(med_school, school_info):
    med_with_info = pd.merge(med_school, school_info, left_on='SCH_PARTY_ID', right_on='PARTY_ID_SCHOOL', how='left').drop_duplicates()

    med_with_info = sort_by_date(med_with_info)
    med_with_info = sort_by_status(med_with_info)

    singular_schools = med_with_info.drop_duplicates('PARTY_ID', keep=False)
    multiple_schools = med_with_info[med_with_info.duplicated('PARTY_ID', keep=False)]
    filtered_schools = multiple_schools.drop_duplicates('PARTY_ID', keep='last')
    med_with_info_2 = pd.concat([singular_schools, filtered_schools])
    return med_with_info_2

def sort_by_date(med_with_info):
    date_list = []
    for row in med_with_info.itertuples():
        try:
            new_date = datetime.datetime.strptime(str(row.GRAD_DT), '%Y-%m-%d')
        except:
            new_date = None
        date_list.append(new_date)
    med_with_info['GRAD_DATE'] = date_list
    med_with_info = med_with_info.sort_values('GRAD_DATE')
    return med_with_info

def sort_by_status(med_with_info):
    countries = []
    statuses = []
    for row in med_with_info.itertuples():
        country = 0
        status = 0
        if row.COUNTRY_ID == 6705:
            country = 1
        if row.STS_TYPE_ID == 9:
            status = 2
        if row.STS_TYPE_ID == 54:
            status = 1
        countries.append(country)
        statuses.append(status)
    med_with_info['COUNTRY'] = countries
    med_with_info['STATUS'] = statuses
    med_with_info = med_with_info.sort_values(['STATUS','COUNTRY','GRAD_DATE'])
    return med_with_info

def create_education_data(education_data, ov_me):
    universe = pd.merge(education_data[0], ov_me[['medical_education_number', 'type']], left_on='ME', right_on='medical_education_number')

    education_data[6] = transform_org_names(education_data[6])
    school_info = transform_school_ids(education_data)
    gme_with_info = transform_gme(education_data)
    med_with_info_2 = transform_med_school(education_data[3], school_info)

    all_education = pd.merge(universe, education_data[5], on='PARTY_ID', how='left')
    all_education = pd.merge(all_education, med_with_info_2, on='PARTY_ID',how='left')
    all_education = pd.merge(all_education, gme_with_info, on='PARTY_ID', how='left', suffixes = ['_SCH', '_GME'])
    return all_education

#analyze
def measure_education(all_education):
    today = datetime.date.today()
    types = ['Physician','Student','Resident']
    all_mes = list(all_education.ME)
    us_schools = list(all_education[(all_education.COUNTRY_ID_SCH==6705)].ME)
    us_gmes = list(all_education[(all_education.COUNTRY_ID_GME==6705)].ME)
    elements = [
        {'data_element': 'Medical School Name',
        'element':'ORG_NM_SCH',
        'null': [''],
        'universe': all_mes},
        {'data_element': 'Medical School State',
        'element':'STATE_ID_SCH',
        'null': ['',-1],
        'universe': us_schools},
        {'data_element': 'Medical School Country',
        'element':'COUNTRY_ID_SCH',
        'null': ['',-1],
        'universe': all_mes},
        {'data_element': 'Medical School Grad Date',
        'element':'GRAD_DT',
        'null': ['',-1, datetime.date(1900, 1, 30)],
        'universe': all_mes},
        {'data_element': 'Education Status',
        'element':'STS_TYPE_ID',
        'null': ['',-1,61,43],
        'universe': all_mes},
        {'data_element': 'Medical Degree',
        'element':'DEGREE_CD',
        'null': [''],
        'universe': all_mes},
        {'data_element': 'GME Institution',
        'element':'ORG_NM_GME',
        'null': [''],
        'universe': all_mes},
        {'data_element': 'GME Institution State',
        'element':'STATE_ID_GME',
        'null': ['',-1],
        'universe': us_gmes},
        {'data_element': 'GME Begin Date',
        'element':'BEGIN_DT',
        'null': ['',-1],
        'universe': all_mes},
        {'data_element': 'GME End Date',
        'element':'END_DT',
        'null': ['',-1],
        'universe': all_mes},
        {'data_element': 'GME Primary Specialty',
        'element':'PRIM_SPEC_ID',
        'null': ['',-1,1883],
        'universe':all_mes},
        {'data_element': 'GME Secondary Specialty',
        'element':'SEC_SPEC_ID',
        'null': ['',-1,1883],
        'universe': all_mes},
        {'data_element': 'GME Training Type',
        'element':'TRAIN_TYPE',
        'null': ['',-1],
        'universe': all_mes},
        {'data_element': 'GME Confirmation Status',
        'element':'CONF_STS_ID',
        'null': ['',-1],
        'universe': all_mes},
        {'data_element': 'GME Status Type',
        'element':'GME_STS_TYPE_CD',
        'null': ['',-1],
        'universe':all_mes},
        {'data_element': 'GME Year in Program',
        'element':'PROG_YEAR',
        'null': ['',-1],
        'universe':all_mes},
        {'data_element': 'GME Post Grad Year',
        'element':'PROG_GRAD_YR',
        'null': ['',-1],
        'universe':all_mes}
    ]
    dict_list = []
    for typo in types:
        for element in elements:
            universe = len(all_education[(all_education.type==typo)&(all_education.ME.isin(element['universe']))])
            complete = len(all_education[(all_education.type==typo)&~(all_education[element['element']].isna())&(all_education.ME.isin(element['universe']))])
            true_complete = len(all_education[(all_education.type==typo)&~(all_education[element['element']].isin(element['null']))&~(all_education[element['element']].isna())&(all_education.ME.isin(element['universe']))])
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

#load
def load(dict_list):
    out_folder = os.environ.get('LOCAL_OUT')
    pd.DataFrame(dict_list).to_csv(f'{out_folder}/Education_Completeness_{str(datetime.date.today())}.csv', index=False)

def get_education_completeness():
    LOGGER.info('Loading MEs from OneView...')
    ov_me = get_oneview_me()
    LOGGER.info('Loading education data from EDW...')
    education_data = get_education_data()
    LOGGER.info('Transforming education data...')
    all_education = create_education_data(education_data, ov_me)
    LOGGER.info('Calculating education data completeness...')
    dict_list = measure_education(all_education)
    LOGGER.info('Loading results...')
    load(dict_list)

if __name__ == "__main__":
    get_education_completeness()