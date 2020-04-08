'''
This script cleans and concatenates disparate DHC data files
'''
from datetime import date
import os
import pandas as pd
import dotenv
import pyodbc

ENV_PATH = 'C:\hsg-data-labs\Sandbox\DHC\env_template.env'
dotenv.load_dotenv(dotenv_path=ENV_PATH)

#Set today
TODAY = str(date.today())

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

#Connect to database
print('Connecting to database...')
CONNECTION = "DSN=PRDDW; UID={}; PWD={}".format('vigrose', 'slytherin10946')
AMAEDW = pyodbc.connect(CONNECTION)

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
NPI = pd.read_sql(con=AMAEDW, sql=NPI_QUERY)
ME = pd.read_sql(con=AMAEDW, sql=ME_QUERY)

#Make id conversion table
NPI_TO_ME = pd.merge(NPI, ME, on='PARTY_ID')[['NPI', 'ME']]

#Concat all dhc
print('Cleaning...')
ALL_DHC = pd.concat([AK_AZ, CA_DE, FL_KY, LA_NH, NJ_OR, PA_TX, UT_WY])

#Add ME
ALL_DHC['NPI'] = ALL_DHC['NPI'].astype(str)
DHC = pd.merge(NPI_TO_ME, ALL_DHC, on='NPI', how='right')

#Save
print('Saving...')
DHC.to_csv(f'{DHC_OUT_DIR}/DHC_{TODAY}.csv', index=False)
