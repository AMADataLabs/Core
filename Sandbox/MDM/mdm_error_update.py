import pandas as pd
import settings
import jira_updates
import pyodbc
import os
import logging
import useful_functions as use
from datetime import datetime, date
import warnings
warnings.simplefilter(action='ignore')

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def get_errors():
    LOGGER.info('Getting unmonitored errors...')
    password = os.environ.get('CREDENTIALS_MDM_PASSWORD')
    username = os.environ.get('CREDENTIALS_MDM_USERNAME')
    w = "DSN=prdMDM; UID={}; PWD={}".format(username, password)
    STG = pyodbc.connect(w)
    error_query = os.environ.get('ERROR_QUERY')
    errors = pd.read_sql(con=STG, sql=error_query)
    LOGGER.info(f'{len(errors)} unmonitored error entries in state License Rejects table')
    errors = errors.fillna('')
    errors['ERROR'] = errors.REJECT_DATE.astype(str) + ' ' + errors.SRC + ' ' + errors.ERROR_DESCRIPTION
    return errors

def get_error_info(errors):
    error_dict = {}
    for row in errors.itertuples():
        if row.ERROR in error_dict.keys():
            error_dict[row.ERROR]['PKEY_DATA'].append(row.PKEY_SRC_OBJECT)
            error_dict[row.ERROR]['COUNT']+=1
            if row.DATA_VALUE != '' and row.DATA_VALUE not in error_dict[row.ERROR]['DATA_VALUES']:
                error_dict[row.ERROR]['DATA_VALUES'].append(row.DATA_VALUE)
        else:
            error_dict[row.ERROR] = {}
            error_dict[row.ERROR]['PKEY_DATA'] = [row.PKEY_SRC_OBJECT]
            error_dict[row.ERROR]['COUNT'] = 1
            error_dict[row.ERROR]['DATE'] = row.REJECT_DATE
            error_dict[row.ERROR]['STATE'] = row.SRC
            error_dict[row.ERROR]['ERROR_DESCRIPTION'] = row.ERROR_DESCRIPTION
            if row.DATA_VALUE != '':
                error_dict[row.ERROR]['DATA_VALUES'] = [row.DATA_VALUE]
            else:
                error_dict[row.ERROR]['DATA_VALUES'] = []
    return error_dict

def create_jira_connection():
    token = os.environ.get('TOKEN')
    base_url = os.environ.get('BASe_URL')
    email = os.environ.get('EMAIL')
    project_id = os.environ.get('PROJECT_ID')
    project_name = os.environ.get('JIRA_PROJECT_NAME')
    project_folder = os.environ.get('LOCAL_OUT')

    parameters = jira_updates.JiraProjectParameters(token, base_url, email, project_id, project_name, project_folder)
    board = jira_updates.JiraProject(parameters)
    return board

def get_cursor(username, password, database):
    w = "DSN={}; UID={}; PWD={}".format(database, username, password)
    STG = pyodbc.connect(w)
    cursor = STG.cursor()
    return STG, cursor
    
def update_db_jira_issue(connection, cursor, ticket):
    query = f'''
    UPDATE STG.MDM_STATELICENSE_REJECTS_HIST
    SET JIRA_ISSUE = {ticket['JIRA_ISSUE_KEY']}
    WHERE 
    REJECT_DATE = {ticket['DATE']}
    AND 
    SRC = {ticket['STATE']}
    AND
    ERROR_DESCRIPTION = {ticket['ERROR_DESCRIPTION']}
    '''
    cursor.execute(query)
    connection.commit()
    
def update_db_jira_status(connection, cursor, issue, status):
    query = f'''
    UPDATE STG.MDM_STATELICENSE_REJECTS_HIST
    ERROR_STATUS = {status}
    WHERE 
    JIRA_ISSUE = {issue}
    '''
    cursor.execute(query)
    connection.commit()

def update_jira(error_tickets, error_dict):
    jira_ref = {}
    for error_ticket in error_tickets:
        pkeys = error_dict[error_ticket]['PKEY_DATA']
        count = error_dict[error_ticket]['COUNT']
        date_ = str(error_dict[error_ticket]['DATE'])
        state = error_dict[error_ticket]['STATE']
        message = error_dict[error_ticket]['ERROR_DESCRIPTION']
        data_values = error_dict[error_ticket]['DATA_VALUES']
        
        if len(data_values) == 1:
            message = message + ' ' + data_values[0]
            data_value_file = False
        else:
            data_value_file = f'{project_folder}/{error_ticket} DATA VALUES.txt'
            with open(data_value_file, 'w') as fp:
                fp.write("\n".join(str(item) for item in pkeys)) 
        
        error_summary = f'{message}, happened on {date_} for {count} records from {state}'
        print(error_summary)
        error_desc = jira_updates.create_description(error_ticket)
        
        new_issue = dqt.create_issue(error_desc, error_summary)
        
        issue_key = new_issue['key']
        issue_id = new_issue['id']
        error_dict[error_ticket]['JIRA_ISSUE_KEY'] = issue_key
        error_dict[error_ticket]['JIRA_ISSUE_ID'] = issue_id
        jira_ref[issue_key] = error_ticket
        update_db_jira_issue(cursor, error_dict[error_ticket])
        
        filename = f'{project_folder}/{error_ticket}.txt'
        
        with open(filename, 'w') as fp:
            fp.write("\n".join(str(item) for item in pkeys))
            
        dqt.add_file(filename, issue_key)
        
        if data_value_file:
            dqt.add_file(data_value_file, issue_key)
            
        print('')


def update_mdm():
    #update jira status on table
    current_jira_status = []
    for row in current_jira.itertuples():
        jira_issue = row.KEY
        if jira_issue not in jira_ref.keys():
            continue
            print (jira_issue)
        status = row.STATUS
        error_sum = jira_ref[jira_issue]
        if status == 'To Do':
            status_cd = 'T'
        elif status == 'In Progress - MDM':
            status_cd = 'M'
        elif status == 'In Progress - IT':
            status_cd = 'I'
        elif status == 'Reporter Review':
            status_cd = 'R'
        else:
            status_cd = 'D'
        new_dict = {
            'JIRA_ISSUE': jira_issue,
            'ERROR_STATUS': status_cd,
            'ERROR': error_sum
        }
        current_jira_status.append(new_dict)
        update_db_jira_status(cursor, jira_issue, status_cd)
    current_jira_status = pd.DataFrame(current_jira_status)


#save state
today = str(date.today())
mdm_load_file = pd.merge(current_jira_status, errors, on='ERROR', suffixes = ['','_OLD'])[errors.columns]
mdm_load_file.drop(columns=['ERROR'])



STG, cursor = get_cursor(username, password_edw, 'tstmdm')
current_jira = dqt.get_snapshot()