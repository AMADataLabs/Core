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


def get_credentials_data():
    with EDW() as edw:
        party_ids = edw.read(os.environ.get('PARTY_ID_QUERY'))
        abms = edw.read(os.environ.get('BOARD_QUERY'))
        license = edw.read(os.environ.get('LICENSE_QUERY'))
        dea = edw.read(os.environ.get('DEA_QUERY'))
        npi = edw.read(os.environ.get('NPI_QUERY'))
    credentials_data = [party_ids, abms, license, dea, npi]
    return credentials_data

def transform_credentials_data(credentials_data, ov_me):
    universe = pd.merge(credentials_data[0], ov_me, left_on='ME', right_on='medical_education_number')
    all_abms = pd.merge(universe, credentials_data[1], left_on='PARTY_ID', right_on='PARTY_ID_FROM').drop_duplicates('CERTIF_ID')
    all_license = pd.merge(universe, credentials_data[2], on='PARTY_ID').drop_duplicates()
    all_license = all_license.drop_duplicates(['LIC_NBR','DEGREE_CD','STATE_ID','PARTY_ID'])
    all_dea = pd.merge(universe, credentials_data[3], on='PARTY_ID').drop_duplicates()
    all_npi = pd.merge(universe, credentials_data[4], on='PARTY_ID').drop_duplicates()
    all_credentials_data = [all_abms, all_license, all_dea, all_npi]
    return all_credentials_data

def measure_license(dict_list, license_data):
    all_mes = list(license_data.ME)
    elements = [
        {'data_element': 'SLN License State',
        'element':'STATE_ID',
        'null': ['',-1],
        'universe': all_mes},
        {'data_element': 'SLN License Status',
        'element':'STS_TYPE_ID',
        'null': ['',43,-1],
        'universe': all_mes},
        {'data_element': 'SLN License Type',
        'element':'LIC_TYPE_ID',
        'null': ['',-1],
        'universe': all_mes},
        {'data_element': 'SLN Issue Date',
        'element':'ISS_DT',
        'null': ['',-1],
        'universe': all_mes},
        {'data_element': 'SLN Expiration Date',
        'element':'EXP_DT',
        'null': ['',-1],
        'universe': all_mes},
        {'data_element': 'SLN Renewal Date',
        'element':'RNW_DT',
        'null': ['',-1],
        'universe': all_mes},
        {'data_element': 'SLN License Degree',
        'element':'DEGREE_CD',
        'null': ['',-1],
        'universe': all_mes}
    ]

    for typo in types:
        total = len(license_data[license_data.type==typo])
        for element in elements:
            universe = len(license_data[(license_data.type==typo)&(license_data.ME.isin(element['universe']))])
            complete = len(license_data[(license_data.type==typo)&~(license_data[element['element']].isna())&(license_data.ME.isin(element['universe']))])
            true_complete = len(license_data[(license_data.type==typo)&~(license_data[element['element']].isin(element['null']))&~(license_data[element['element']].isna())&(license_data.ME.isin(element['universe']))])
            new_dict = {
                'Universe': typo,
                'Data Element': element['data_element'],
                'Complete': complete,
                'Complete and Known': true_complete,
                'Universe Total': universe,
                'Measure':'Completeness',
                'Credential':'SLN'
            }
            dict_list.append(new_dict)
    return dict_list

def measure_credentials(credentials_data):
    today = datetime.date.today()
    types = ['Physician','Student','Resident']
    'Date': today

def load(dict_list):
    out_folder = os.environ.get('LOCAL_OUT')
    pd.DataFrame(dict_list).to_csv(f'{out_folder}/Credentials_Completeness_{str(datetime.date.today())}.csv', index=False)

def get_credentials_completeness():
    LOGGER.info('Loading MEs from OneView...')
    ov_me = measurement.get_oneview_me()
    LOGGER.info('Loading credentials data from EDW...')
    credentials_data = get_credentials_data()
    LOGGER.info('Transforming credentials data...')
    all_credentials = transform_credentials_data(credentials_data, ov_me)


    LOGGER.info('Calculating person data completeness...')
    dict_list = measure_credentials(all_credentials)
    LOGGER.info('Loading results...')
    load(dict_list)

if __name__ == "__main__":
    get_credentials_completeness()