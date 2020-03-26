'''
This script grabs the most recent DEA data
'''
import pandas as pd
import pyodbc
from auth import username, password


Credentials = "DSN=PRDDW; UID={}; PWD={}".format(username, password)
AMAEDW = pyodbc.connect(s)

sql_query = \
    """ 
    SELECT DISTINCT
    D.PARTY_ID, 
    D.REPORTED_NM AS NAME,
    D.FROM_DT,
    P.ADDR_1, 
    P.ADDR_2, 
    P.ADDR_3, 
    P.CITY, 
    S.SRC_STATE_CD AS STATE_CD, 
    P.POST_CD AS ZIP
    FROM 
    AMAEDW.POST_CD P, AMAEDW.STATE S, AMAEDW.DEA_REG D
    WHERE  
    D.POST_CD_ID = P.POST_CD_ID 
    AND
    P.STATE_ID = S.STATE_ID
    ORDER BY D.FROM_DT DESC;
    """

dea = pd.read_sql(con=AMAEDW, sql=sql_query)
DEA = dea.drop_duplicates(subset = 'PARTY_ID', keep='first')
print(dea.shape)
dea.head()

DEA.to_csv('DEA_dump.csv')