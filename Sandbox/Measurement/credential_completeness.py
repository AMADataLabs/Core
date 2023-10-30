import settings
import measurement
import credential_data
import connection
import pandas as pd
import os
import logging
from datetime import date

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def npi_completeness(data_file, methods_df, path):
    today = str(date.today())
    data = pd.read_csv(data_file, low_memory=False)
    data_dict = data.to_dict('records')
    complete_list = []
    for row in data_dict:
        complete_list += measurement.measure_row(row, methods_df, 'COMPLETENESS')
    cred_completeness = pd.DataFrame(complete_list) 
    cred_filename = f'{path}NPI_Completeness_{today}.csv'
    cred_completeness.to_csv(cred_filename, index=False)

    return cred_completeness

def dea_completeness(data_file, methods_df, path):
    today = str(date.today())
    data = pd.read_csv(data_file, low_memory=False)
    data_dict = data.to_dict('records')
    complete_list = []
    for row in data_dict:
        complete_list += measurement.measure_row(row, methods_df, 'COMPLETENESS')
    cred_completeness = pd.DataFrame(complete_list) 
    cred_filename = f'{path}DEA_Completeness_{today}.csv'
    cred_completeness.to_csv(cred_filename, index=False)

    return cred_completeness

def abms_completeness(data_file, methods_df, path):
    today = str(date.today())
    data = pd.read_csv(data_file, low_memory=False)
    data_dict = data.to_dict('records')
    complete_list = []
    for row in data_dict:
        complete_list += measurement.measure_row(row, methods_df, 'COMPLETENESS')
    cred_completeness = pd.DataFrame(complete_list) 
    cred_filename = f'{path}ABMS_Completeness_{today}.csv'
    cred_completeness.to_csv(cred_filename, index=False)

    return cred_completeness

def license_completeness(data_file, methods_df, path):
    today = str(date.today())
    data = pd.read_csv(data_file, low_memory=False)
    data_dict = data.to_dict('records')
    complete_list = []
    for row in data_dict:
        complete_list += measurement.measure_row(row, methods_df, 'COMPLETENESS')
    cred_completeness = pd.DataFrame(complete_list) 
    cred_filename = f'{path}License_Completeness_{today}.csv'
    cred_completeness.to_csv(cred_filename, index=False)

    return cred_completeness

def credentials_completeness(get_new_data):
    path = os.environ.get('LOCAL_OUT')
    methods_df = connection.get_measurement_methods()
    if get_new_data:
        data_files = credential_data.credentials()
    else:
        npi_file = connection.get_newest(path,'Data_NPI')
        abms_file = connection.get_newest(path,'Data_ABMS')
        lic_file = connection.get_newest(path,'Data_License')
        dea_file = connection.get_newest(path,'Data_DEA')
        data_files = [abms_file, lic_file, dea_file, npi_file]
        
    abms_completeness(data_files[0], methods_df, path)
    license_completeness(data_files[1], methods_df, path)
    dea_completeness(data_files[2], methods_df, path)
    npi_completeness(data_files[3], methods_df, path)
        

if __name__ == "__main__":
    credentials_completeness(get_new_data=False)