'''
This script cleans and concatenates disparate DHC data files
'''
from datetime import date
import os
import pandas as pd
import settings
from datalabs.access.edw import EDW

#Set today
TODAY = str(date.today())[0:7]

#Set file locations
AK_AZ_FILE = os.getenv('PHYSICIANS_AK_AZ')
CA_DE_FILE = os.getenv('PHYSICIANS_CA_DE')
FL_KY_FILE = os.getenv('PHYSICIANS_FL_KY')
LA_NH_FILE = os.getenv('PHYSICIANS_LA_NH')
NJ_OR_FILE = os.getenv('PHYSICIANS_NJ_OR')
PA_TX_FILE = os.getenv('PHYSICIANS_PA_TX')
UT_WY_FILE = os.getenv('PHYSICIANS_UT_WY')
DHC_OUT_DIR = os.getenv('DHC_OUT_FOLDER')

#Make dataframes
print('Reading Files...')
AK_AZ = pd.read_csv(AK_AZ_FILE)
CA_DE = pd.read_csv(CA_DE_FILE)
FL_KY = pd.read_csv(FL_KY_FILE)
LA_NH = pd.read_csv(LA_NH_FILE)
NJ_OR = pd.read_csv(NJ_OR_FILE)
PA_TX = pd.read_csv(PA_TX_FILE)
UT_WY = pd.read_csv(UT_WY_FILE)

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

#Concat all dhc
print('Cleaning...')
ALL_DHC = pd.concat([AK_AZ, CA_DE, FL_KY, LA_NH, NJ_OR, PA_TX, UT_WY])

#Add ME
ALL_DHC['NPI'] = ALL_DHC['NPI'].astype(str)
DHC = pd.merge(NPI_TO_ME, ALL_DHC, on='NPI', how='right')

#Fix phones
ALL_DHC.columns = [c.replace(' ','_') for c in ALL_DHC.columns.values]
ALL_DHC = ALL_DHC.fillna('None')
ALL_DHC['Phone_Number'] = ALL_DHC['Phone_Number'].apply(lambda x: x.replace('.',''))

#Save
print('Saving...')
DHC.to_csv(f'{DHC_OUT_DIR}/DHC_{TODAY}.csv', index=False)
