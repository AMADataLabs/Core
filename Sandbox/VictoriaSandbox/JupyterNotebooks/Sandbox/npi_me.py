import pandas as pd
import pyodbc

def get_npi_to_me():
    username = 'vigrose'
    password_edw = 'Gryffindor~10946'

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
    w = "DSN=PRDDW; UID={}; PWD={}".format(username, password_edw)
    AMAEDW = pyodbc.connect(w)
    NPI = pd.read_sql(con=AMAEDW, sql=NPI_QUERY)
    ME = pd.read_sql(con=AMAEDW, sql=ME_QUERY)

    #Make id conversion table
    NPI_TO_ME = pd.merge(NPI, ME, on='PARTY_ID')[['NPI', 'ME']]

    return NPI_TO_ME