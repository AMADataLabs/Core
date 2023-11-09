import pandas as pd
import psycopg2
import pyodbc
import logging
import os
import settings

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

def edw_connect():
    username = os.environ.get('CREDENTIALS_EDW_USERNAME')
    password_edw = os.environ.get('CREDENTIALS_EDW_PASSWORD')
    w = "DSN=PRDDW; UID={}; PWD={}".format(username, password_edw)
    AMAEDW = pyodbc.connect(w)
    return AMAEDW

def get_newest(path, text):
    '''Get newest filename'''
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if text in basename]
    return max(paths, key=os.path.getctime)

def get_oneview_me(): 
    conn = oneview_connect()
    ov_me_sql = os.environ.get('ONEVIEW_ME')
    ov_me = pd.read_sql_query(ov_me_sql, conn)
    return ov_me

def get_measurement_methods():
    folder = os.environ.get('LOCAL_OUT')
    measurement_methods_file = f'{folder}Measurement_Methods.xlsx'
    measurement_methods = pd.read_excel(measurement_methods_file)
    print(measurement_methods_file)
    return measurement_methods

def fix_me(me_list):
    nums = []
    for num in me_list:
        num = str(num).replace('.0','')
        num = '{:0>11}'.format(num)
        nums.append(num)
    return nums