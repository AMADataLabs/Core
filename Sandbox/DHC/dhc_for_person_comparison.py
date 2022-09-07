'''
This script cleans and concatenates disparate DHC data files
'''
from datetime import date
import os
import pandas as pd
import settings
from pathlib import Path
from datalabs.access.edw import EDW

#Set today
TODAY = str(date.today())[0:7]

#Make dataframes
print('Reading Files...')

DOWNLOADS = os.getenv('DOWNLOADS') 
file_list = []
ALL_DHC = pd.DataFrame()
for file in os.listdir(DOWNLOADS):
    if file.startswith('Person'):
        file_name = f'{DOWNLOADS}/{file}'
        print(file_name)
        new_file = pd.read_csv(file_name, error_bad_lines=False)
        ALL_DHC = pd.concat([ALL_DHC, new_file])


#Set file locations
DHC_OUT_DIR = os.getenv('DHC_OUT_FOLDER')
LOCAL_DHC_OUT_DIR = os.getenv('LOCAL_DHC_OUT_FOLDER')

print('Reading EDW...')
#Write queries
ME_QUERY = \
    """
    SELECT DISTINCT
    P.PARTY_ID,
    P.KEY_VAL AS ME
    FROM
    AMAEDW.PARTY_KEY P
    WHERE
    P.KEY_TYPE_ID = 18
    AND
    P.ACTIVE_IND = 'Y'
    """

NPI_QUERY = \
    """
    SELECT DISTINCT
    P.PARTY_ID,
    P.KEY_VAL AS NPI
    FROM
    AMAEDW.PARTY_KEY P
    WHERE
    P.KEY_TYPE_ID = 38
    AND
    P.ACTIVE_IND = 'Y'
    """
#Execute queries
with EDW() as edw:
    NPI = edw.read(NPI_QUERY)
    ME = edw.read(ME_QUERY)

#Make id conversion table
NPI_TO_ME = pd.merge(NPI, ME, on='PARTY_ID')[['NPI', 'ME']]

print('Cleaning...')
# print(len(ALL_DHC))
# ALL_DHC = ALL_DHC.drop_duplicates()
# print(len(ALL_DHC))

#Add ME
ALL_DHC['NPI'] = ALL_DHC['NPI'].astype(str)
DHC = pd.merge(NPI_TO_ME, ALL_DHC, on='NPI', how='right')

#Fix phones
ALL_DHC.columns = [c.replace(' ','_') for c in ALL_DHC.columns.values]
ALL_DHC = ALL_DHC.fillna('None')

#Save
print('Saving...')
DHC.to_csv(f'{LOCAL_DHC_OUT_DIR}/DHC_PERSON{TODAY}.csv', index=False)