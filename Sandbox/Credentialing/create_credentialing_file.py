'''Functions to extract datamart data'''
import os
from datetime import date, datetime
import pandas as pd
import pyodbc
import settings
from dateutil.relativedelta import relativedelta
from datalabs.access.datamart import DataMart
import logging
import useful_functions as use

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

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
    LOGGER.info("Getting addresses...")
    org_addresses = pd.read_sql(con=SSO, sql=query)
    org_addresses['ADVANTAGE_ID'] = org_addresses.ADVANTAGE_ID.fillna('0')
    org_addresses = org_addresses[org_addresses.ADVANTAGE_ID!='']
    org_addresses['CUSTOMER_NBR']=[float(x) for x in org_addresses.ADVANTAGE_ID]
    org_addresses = org_addresses.sort_values('STATUS').drop_duplicates('ADVANTAGE_ID', keep='last')
    return org_addresses

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

def get_datamart_results():
    with DataMart() as datamart:
        LOGGER.info("Getting customers...")
        customers = datamart.get_customers()
        LOGGER.info("Getting orders...")
        orders = datamart.get_orders()
    customers = customers.fillna('None')
    customers = customers[customers.CUSTOMER_NAME != 'None']
    customers['CUSTOMER_KEY'] = customers.CUSTOMER_KEY.astype(str)
    results = pd.merge(orders, customers, on='CUSTOMER_KEY').drop_duplicates()
    results.CUSTOMER_NBR = results.CUSTOMER_NBR.astype(float)
    return results

def get_results():
    results = get_datamart_results()
    addresses = get_addresses()
    all_results = pd.merge(addresses, results, on='CUSTOMER_NBR')
    return all_results

def get_previous_date():
    out = os.environ.get('OUTPUT_FOLDER')
    previous_file = use.get_newest(out, 'address_load_profile_orders')
    previous_datetime = datetime.strptime(previous_file[-14:-4], "%Y-%m-%d")
    previous_date = previous_datetime.date()
    return previous_date

def generate_file():
    '''Generate file for loading'''
    today = str(date.today())
    all_results = get_results()
    out = os.environ.get('OUTPUT_FOLDER')
    udrive = os.environ.get('UDRIVE_FOLDER')
    previous_date = get_previous_date()
    all_results = all_results[(all_results.FULL_DT) > previous_date]
    all_results = all_results.drop_duplicates(['ME','CUSTOMER_KEY'])
    acceptable_customers = ['Ambulatory Care',
                            'Hospital',
                            'Group',
                            'Government',
                            'Health Related',
                            'Government',
                            'Long Term Care',
                            'Managed Care']
    all_results = all_results[all_results.CUSTOMER_CATEGORY_DESC.isin(acceptable_customers)]
    col_rename = {
        'ADDRESS_LINE_1':'addr_line_1',
        'CITY':'addr_city',
        'STATE':'addr_state',
        'ADDRESS_LINE_2':'addr_line_2'
    }
    all_results = all_results.rename(columns=col_rename)
    cols = ['entity_id',
            'me#',
            'comm_id',
            'usage',
            'load_type',
            'addr_type',
            'addr_line_1',
            'addr_line_2',
            'addr_line_3',
            'addr_city',
            'addr_state',
            'addr_zip',
            'addr_plus4',
            'addr_country',
            'source',
            'source_dtm'
            ]
    all_results['me#'] = fix_me(all_results.ME)
    all_results['addr_zip'] = [use.fix_zipcode(x) for x in all_results.ZIPCODE]
    all_results['addr_plus4'] = [x[-4:] if len(str(x))==9 else '' for x in all_results.ZIPCODE]
    all_results['load_type'] = 'A'
    all_results['addr_type'] = 'OF'
    all_results['source'] = 'CRED-ADDR'
    all_results['source_dtm'] = today
    all_results['entity_id'] = ''
    all_results['comm_id'] = ''
    all_results['usage'] = ''
    all_results['addr_country'] = ''
    all_results['addr_line_3'] = ''
    all_results[cols].sample(1000).to_csv(f'{out}Credentialing_Addresses_Sample_{today}.csv',
                                          index=False)

    all_results[cols].to_csv(f'{out}address_load_profile_orders_{today}.csv', index=False)
    all_results[cols].to_csv(f'{udrive}address_load_profile_orders_{today}.csv', index=False)
    all_results.to_csv(f'{out}Credentialing_Addresses_latest.csv', index=False)

def generate_triangulation_file():
    '''Create file for triangulation'''
    today = date.today()
    all_results = get_results()
    out = os.environ.get('OUTPUT_FOLDER')
    one_year_ago = date.today() - relativedelta(years=2)
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
    LOGGER.info('Saving...')
    new_results.to_csv(f'{out}Credentialing_Addresses_{str(today)}.csv', index=False)

if __name__ == "__main__":
    generate_file()
