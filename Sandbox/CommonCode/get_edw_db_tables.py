# Kari Palmier    8/27/19    Created 
#
#############################################################################
import pandas as pd
import pyodbc

import datalabs.curate.dataframe as df


def get_edw_connection(username, password):
    # DSN=<odbc driver name for EDW> view your odbc sources to find the name and change if necessary.
    # Might need to be reworked
    EDW_conn = pyodbc.connect('DSN=EDW; UID={}; PWD={}'.format(username, password))
    EDW_conn.execute('SET ISOLATION TO DIRTY READ;')
    
    return EDW_conn

def get_npi_me_mapping(EDW_conn):
    
    # Execute query that returns ME numbers and their corresponding NPI numbers and party IDs
    npi_me_query = \
        """
        SELECT
        K1.KEY_VAL AS ME,
        K2.KEY_VAL AS NPI_NBR,
        K1.PARTY_ID
        FROM
        AMAEDW.PARTY_KEY K1, AMAEDW.PARTY_KEY K2
        WHERE
        K1.KEY_TYPE_ID=18
        AND
        K1.ACTIVE_IND='Y'
        AND
        K1.PARTY_ID=K2.PARTY_ID
        AND
        K2.KEY_TYPE_ID=38
        AND
        K2.ACTIVE_IND='Y'
        """    
    npi_me_df = pd.read_sql(npi_me_query, EDW_conn)
    
    npi_me_df = df.strip(npi_me_df)

    return npi_me_df


def get_party_keys(EDW_conn, key_type_id):
    
    # Execute query that returns ME numbers and their corresponding NPI numbers and party IDs
    party_key_query = \
        """
            SELECT PARTY_ID, KEY_VAL
            FROM AMAEDW.PARTY_KEY
            where KEY_TYPE_ID = {};
        """.format(key_type_id)    
        
    party_key_df = pd.read_sql(party_key_query, EDW_conn)
    
    party_key_df = df.strip(party_key_df)

    return party_key_df


def get_active_gradschool_name(EDW_conn):
    
    # Execute query that returns ME numbers and their corresponding NPI numbers and party IDs
    act_grad_name_query = \
        """
            SELECT PARTY_ID, ORG_NM as MEDSCHOOL_NAME
            FROM AMAEDW.ORG_NM
            where THRU_DT IS NULL;
        """    
    act_grad_name_df = pd.read_sql(act_grad_name_query, EDW_conn)
    
    act_grad_name_df = df.strip(act_grad_name_df)

    return act_grad_name_df


def get_edw_post_addr_data(EDW_conn):
    
    # Execute query that returns ME numbers and their corresponding NPI numbers and party IDs
    addr_query = \
        """
            SELECT POST_CD_ID, SRC_POST_KEY, ADDR_1, ADDR_2, CITY,
            SRC_STATE_CD, POST_CD, POST_CD_PLUS_4
            FROM AMAEDW.POST_CD P, AMAEDW.STATE S
            WHERE P.STATE_ID = S.STATE_ID;
        """    
    addr_df = pd.read_sql(addr_query, EDW_conn)
    
    addr_df = df.strip(addr_df)

    return addr_df
