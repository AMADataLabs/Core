#import dependencies
import pyodbc
import pandas as pd

#for aims
v = 'DSN=aims_prod; UID={}; PWD={}'.format(username, password_aims)
AIMS_conn = pyodbc.connect(v)
AIMS_conn.execute('SET ISOLATION TO DIRTY READ;')

#for edw
s = "DSN=PRDDW; UID={}; PWD={}".format(username, password_edw)
AMAEDW = pyodbc.connect(s)


#for ods test
w = "DSN=etstods; UID={}; PWD={}".format(username, password_edw)
ODS = pyodbc.connect(w)



#example query
sql_query_1 = \
    """ 
    SELECT *
    FROM 
    AMAEDW.PARTY_KEY P
    WHERE  
    P.KEY_TYPE_ID = 18 
    AND 
    P.ACTIVE_IND = 'Y'
    """
ME = pd.read_sql(con=AMAEDW, sql=sql_query_1)