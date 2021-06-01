'''Functions to extract datamart data'''
import os
from datetime import date
import pandas as pd
import pyodbc
import settings
from datetime import datetime
from dateutil.relativedelta import relativedelta

def org_manager_connect():
    username_ = os.environ.get('ORG_MANAGER_USERNAME')
    password_ = os.environ.get('ORG_MANAGER_PASSWORD')
    x = "DSN=prdsso; UID={}; PWD={}".format(username_, password_)
    SSO = pyodbc.connect(x)
    return SSO

def get_org_query():
    query = \
        '''
        SELECT *
        FROM
        SSO.ORGANIZATION
        '''
    return query

def get_addresses():
    SSO = org_manager_connect()
    query = get_org_query()
    org_addresses = pd.read_sql(con=SSO, sql=query)
    org_addresses['ADVANTAGE_ID'] = org_addresses.ADVANTAGE_ID.fillna('0')
    org_addresses = org_addresses[org_addresses.ADVANTAGE_ID!='']
    org_addresses['CUSTOMER_NBR']=[float(x) for x in org_addresses.ADVANTAGE_ID]
    org_addresses = org_addresses.sort_values('STATUS').drop_duplicates('ADVANTAGE_ID', keep='last')
    return org_addresses

def datamart_connect():
    username = os.environ.get('CREDENTIALS_DATAMART_USERNAME')
    password = os.environ.get('CREDENTIALS_DATAMART_PASSWORD')
    s = "DSN=PRDDM; UID={}; PWD={}".format(username, password)
    AMADM = pyodbc.connect(s)
    return AMADM

def get_order_query():
    '''SQL query to get order table'''
    query = \
    f"""
    SELECT DISTINCT
    D.FULL_DT,
    H.MED_EDU_NBR AS ME,
    H.PARTY_ID,
    O.ORDER_NBR,
    O.ORDER_PRODUCT_ID,
    O.ORDER_PHYSICIAN_HIST_KEY,
    O.CUSTOMER_KEY
    FROM
    AMADM.DIM_DATE D, AMADM.FACT_EPROFILE_ORDERS O, AMADM.DIM_PHYSICIAN_HIST H
    WHERE
    D.DATE_KEY = O.ORDER_DT_KEY
    AND
    H.PHYSICIAN_HIST_KEY = O.ORDER_PHYSICIAN_HIST_KEY
    AND
    D.YR in (2019,2020,2021)
    """
    return query

def get_customer_query():
    '''SQL query to get customer table'''
    query = \
    """
    SELECT DISTINCT
    C.CUSTOMER_KEY,
    C.CUSTOMER_NBR,
    C.CUSTOMER_ISELL_LOGIN,
    C.CUSTOMER_NAME,
    C.CUSTOMER_TYPE_DESC,
    C.CUSTOMER_TYPE,
    C.CUSTOMER_CATEGORY_DESC
    FROM
    AMADM.dim_customer C
    """
    return query

def fix_me(me_list):
    '''Add leading zeroes to ME'''
    nums = []
    for num in me_list:
        num = str(num)
        num = num.replace('.0', '')
        if len(num) == 10:
            num = '0' + num
        elif len(num) == 9:
            num = '00' + num
        elif len(num) == 8:
            num = '000' + num
        nums.append(num)
    return nums

def get_datamart_results(order_type='all', customer_type='all'):
    '''Get results for specific time period'''
    order_query = get_order_query()
    customer_query = get_customer_query()
    AMADM = datamart_connect()
    orders = pd.read_sql(con=AMADM, sql=order_query)
    customers = pd.read_sql(con=AMADM, sql=customer_query)
    customers.CUSTOMER_KEY = customers.CUSTOMER_KEY.astype(str)
    customers = customers.fillna('None')
    if customer_type == 'all':
        class_cust = customers[customers.CUSTOMER_NAME != 'None']
    else:
        class_cust = customers[(customers.CUSTOMER_CATEGORY_DESC.isin(customer_type))&
                               (customers.CUSTOMER_NAME != 'None')]
    if order_type == 'reapp':
        orders = orders[orders.ORDER_PRODUCT_ID.isin([4915514])]
    elif order_type == 'app':
        orders = orders[orders.ORDER_PRODUCT_ID.isin([4915513])]
    else:
        orders = orders[orders.ORDER_PRODUCT_ID.isin([4915513, 4915514])]
    results = pd.merge(orders, class_cust, on='CUSTOMER_KEY').drop_duplicates()
    results.CUSTOMER_NBR = results.CUSTOMER_NBR.astype(float)
    return results

def get_results(order_type='all', customer_type='all'):
    addresses = get_addresses()
    results = get_datamart_results(order_type, customer_type)
    all_results = pd.merge(addresses, results, on='CUSTOMER_NBR')
    return all_results

def generate_file():
    '''Generate file for loading'''
    today = str(date.today())
    all_results = get_results()
    out = os.environ.get('OUTPUT_FOLDER')
    cols = ['me#',
            'load_type',
            'addr_type',
            'addr_line_1',
            'addr_line_2',
            'addr_city',
            'addr_state',
            'addr_zip',
            'source',
            'source_dtm'
            ]
    all_results['me#'] = fix_me(all_results.ME)
    all_results['load_type'] = 'A'
    all_results['addr_type'] = 'OF'
    all_results['source'] = 'CRED-ADDR'
    all_results['source_dtm'] = today
    all_results['addr_line_3'] = ''
    all_results[cols].sample(1000).to_csv(f'{out}Credentialing_Addresses_Sample_{today}.csv',
                                          index=False)

    all_results.to_csv(f'{out}Credentialing_Addresses_{today}.csv', index=False)
    all_results.to_csv(f'{out}Credentialing_Addresses_latest.csv', index=False)

def generate_triangulation_file():
    '''Create file for triangulation'''
    today = date.today()
    all_results = get_results()
    out = os.environ.get('OUTPUT_FOLDER')
    one_year_ago = date.today() - relativedelta(years=1)
    new_results = all_results[(all_results.FULL_DT) > one_year_ago]
    acceptable_customers = ['Ambulatory Care',
                            'Hospital',
                            'Group',
                            'Government',
                            'Health Related',
                            'Government',
                            'Long Term Care',
                            'Managed Care']
    new_results = new_results[new_results.CUSTOMER_CATEGORY_DESC.isin(acceptable_customers)]
    new_results.to_csv(f'{out}Credentialing_Addresses_{str(today)}.csv', index=False)

if __name__ == "__main__":
    generate_triangulation_file()
