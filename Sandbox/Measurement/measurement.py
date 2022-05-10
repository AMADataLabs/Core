import pandas as pd
import psycopg2
import pyodbc
import datetime
import logging
import os
import settings
from datalabs.access.edw import EDW

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

#connect
def oneview_connect():
    conn = psycopg2.connect(
        host = os.environ.get('DATABASE_ONEVIEW_HOST'),
        database = os.environ.get('DATABASE_ONEVIEW_NAME'),
        user = os.environ.get('CREDENTIALS_ONEVIEW_USERNAME'),
        password = os.environ.get('CREDENTIALS_ONEVIEW_PASSWORD'))
    return conn

#read
def get_oneview_me(): 
    conn = oneview_connect()
    ov_me_sql = os.environ.get('ONEVIEW_ME')
    ov_me = pd.read_sql_query(ov_me_sql, conn)
    return ov_me