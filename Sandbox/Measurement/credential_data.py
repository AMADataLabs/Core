import pandas as pd
import datetime
import logging
import os
import settings
import connection

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def get_credentials_data():
    AMAEDW = connection.edw_connect()
    party_ids = pd.read_sql(con=AMAEDW, sql=(os.environ.get('PARTY_ID_QUERY')))
    abms = pd.read_sql(con=AMAEDW, sql=(os.environ.get('BOARD_QUERY')))
    license = pd.read_sql(con=AMAEDW, sql=(os.environ('LICENSE_QUERY')))
    dea = pd.read_sql(con=AMAEDW, sql=(os.environ.get('DEA_QUERY')))
    npi = pd.read_sql(con=AMAEDW, sql=(os.environ.get('NPI_QUERY')))
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

def load(data_list):
    out_folder = os.environ.get('LOCAL_OUT')
    dea_filename = f'{out_folder}/Credential_Data_DEA_{str(datetime.date.today())}.csv'
    abms_filename = f'{out_folder}/Credential_Data_ABMS_{str(datetime.date.today())}.csv'
    lic_filename = f'{out_folder}/Credential_Data_License_{str(datetime.date.today())}.csv'
    npi_filename = f'{out_folder}/Credential_Data_NPI_{str(datetime.date.today())}.csv'
    data_list[0].to_csv(abms_filename, index=False)
    data_list[1].to_csv(lic_filename, index=False)
    data_list[2].to_csv(dea_filename, index=False)
    data_list[4].to_csv(npi_filename, index=False)
    filenames = [abms_filename, lic_filename, dea_filename, npi_filename]
    return filenames

def credentials():
    LOGGER.info('Loading MEs from OneView...')
    ov_me = connection.get_oneview_me()
    LOGGER.info('Loading credentials data from EDW...')
    credentials_data = get_credentials_data()
    LOGGER.info('Transforming credentials data...')
    all_credentials = transform_credentials_data(credentials_data, ov_me)
    LOGGER.info('Loading results...')
    load(all_credentials)

if __name__ == "__main__":
    credentials()