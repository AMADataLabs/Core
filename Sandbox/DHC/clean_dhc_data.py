'''
This script cleans and concatenates disparate DHC data files
'''
from datetime import date
import os
import pandas as pd
import settings
from pathlib import Path
import pyodbc

#Set today
TODAY = str(date.today())[0:7]

#Make dataframes
print('Reading Files...')

DOWNLOADS = os.getenv('DOWNLOAD_FOLDER') 
file_list = []
ALL_DHC = pd.DataFrame()
for file in os.listdir(DOWNLOADS):
    if file.startswith('DQ-'):
        file_name = f'{DOWNLOADS}/{file}'
        print(file_name)
        new_file = pd.read_csv(file_name, error_bad_lines=False)
        ALL_DHC = pd.concat([ALL_DHC, new_file])
print(ALL_DHC.columns)


#Set file locations
DHC_OUT_DIR = os.getenv('DHC_OUT_FOLDER')
# LOCAL_DHC_OUT_DIR = os.getenv('LOCAL_DHC_OUT_FOLDER')

def get_npi_to_me():
    password = os.environ.get('CREDENTIALS_EDW_PASSWORD')
    username = os.environ.get('CREDENTIALS_EDW_USERNAME')
    query = os.environ.get('QUERY')
    w = "DSN=PRDDW; UID={}; PWD={}".format(username, password)
    AMAEDW = pyodbc.connect(w)
    npi_to_me = pd.read_sql(con=AMAEDW, sql=query)
    return npi_to_me

def append_me(new_download):
    print('Appending ME numbers')
    me_npi = get_npi_to_me()
    new_download['NPI_NBR'] = [str(int(x)) for x in new_download.NPI]
    with_mes = pd.merge(new_download, me_npi, on='NPI_NBR', how='left')
    with_mes.drop(columns = ['NPI_NBR'])
    return with_mes

print('Cleaning...')
print(len(ALL_DHC))
ALL_DHC = ALL_DHC.drop_duplicates()
print(len(ALL_DHC))

#Add ME
ALL_DHC = append_me(ALL_DHC)

#Fix phones
ALL_DHC.columns = [c.replace(' ','_') for c in ALL_DHC.columns.values]
ALL_DHC = ALL_DHC.fillna('None')
ALL_DHC['Phone_Number'] = ALL_DHC['Phone_Number'].apply(lambda x: x.replace('.',''))

#Save
print('Saving...')
# ALL_DHC.to_csv(f'{LOCAL_DHC_OUT_DIR}/DHC_{TODAY}.csv', index=False)
ALL_DHC.to_csv(f'{DHC_OUT_DIR}/DHC_{TODAY}.csv', index=False)

