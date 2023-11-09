import pandas as pd
import datetime
import logging
import os
import settings
import connection

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def get_education_data():
    AMAEDW = connection.edw_connect()
    party_ids = pd.read_sql(con=AMAEDW, sql=(os.environ.get('ME_QUERY')))
    more_school_ids = pd.read_sql(con=AMAEDW, sql=(os.environ.get('MORE_SCHOOL_QUERY')))
    school_ids = pd.read_sql(con=AMAEDW, sql=(os.environ.get('SCHOOL_QUERY')))
    med_school = pd.read_sql(con=AMAEDW, sql=(os.environ.get('MED_SCHOOL_QUERY')))
    gme = pd.read_sql(con=AMAEDW, sql=(os.environ.get('GME_QUERY')))
    gme_year= pd.read_sql(con=AMAEDW, sql=(os.environ.get('YEAR_QUERY')))
    org_names = pd.read_sql(con=AMAEDW, sql=(os.environ.get('ORG_QUERY')))
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

def load(data):
    out_folder = os.environ.get('LOCAL_OUT')
    filename = f'{out_folder}/Education_Data_{str(datetime.date.today())}.csv'
    data.to_csv(filename, index = False)
    return filename

def education():
    LOGGER.info('Loading MEs from OneView...')
    ov_me = connection.get_oneview_me()
    LOGGER.info('Loading education data from EDW...')
    education_data = get_education_data()
    LOGGER.info('Transforming education data...')
    all_education = create_education_data(education_data, ov_me)
    LOGGER.info('Loading results...')
    filename = load(all_education)
    LOGGER.info(f'Data saved at {filename}')

if __name__ == "__main__":
    education()