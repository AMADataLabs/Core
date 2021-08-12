import pandas as pd 
import os
import settings
import pyodbc
# from datalabs.access.aims import AIMS
from srs_scrape import scrape_srs
from match import match_missing_ids
import logging
import useful_functions as use
from datetime import date

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def aims_connect():
    username = os.environ.get('AIMS_USERNAME')
    password_aims = os.environ.get('AIMS_PASSWORD')
    s = "DSN=aims_prod; UID={}; PWD={}".format(username, password_aims)
    informix = pyodbc.connect(s)
    return informix

def get_addresses():
    informix = org_manager_connect()
    query = os.environ.get('')
    org_addresses = pd.read_sql(con=SSO, sql=query)

#scraped old
def get_old_scrape(): 
    srs_folder = os.environ.get('OUT_DIR')
    srs_old_file = use.get_newest(srs_folder, 'SRS_Scrape')
    LOGGER.info(f"Retrieving {srs_old_file}...")
    srs_old = pd.read_csv(srs_old_file)
    return srs_old

#scraped new
def find_updates(srs_old, srs_new):
    srs_old['Curr Status Date'] = pd.to_datetime(srs_old['Curr Status Date'])
    srs_new['Curr Status Date'] = pd.to_datetime(srs_new['Curr Status Date'])
    all_scraped = pd.merge(srs_old, srs_new, on='AAMC ID', suffixes = ['_old', ''], how = 'right')
    all_scraped['Time_Diff'] = all_scraped['Curr Status Date'] - all_scraped['Curr Status Date_old']
    updated = all_scraped[all_scraped['Time_Diff']!='0 days'][srs_new.columns]
    new = srs_new[srs_new['AAMC ID'].isin(srs_old['AAMC ID']==False)]
    updates = pd.concat([updated, new]).drop_duplicates()
    return updates

#aamc_found
def match_aamc(scraped):
    LOGGER.info("Getting aamc_ids...")
    informix = aims_connect()
    query = os.environ.get('AAMC_QUERY')
    active_aamc = pd.read_sql(con=informix, sql=query)
    active_aamc['aamc_id'] = active_aamc.aamc_id.astype(int)
    scraped['aamc_id'] = scraped['AAMC ID']
    no_aamc_id = scraped[scraped['AAMC ID'].isin(active_aamc.aamc_id)==False].drop_duplicates('AAMC ID')
    found = pd.merge(scraped, active_aamc, on='aamc_id')
    return found, no_aamc_id

#missing
def get_all_students():
    LOGGER.info("Getting all students...")
    informix = aims_connect()
    query = os.environ.get('STUDENT_QUERY')
    all_students = pd.read_sql(con=informix, sql=query)
    return all_students

#stu_affil
def get_stu_affil(aamc_found):
    LOGGER.info('Getting student affiliates...')
    informix = aims_connect()
    query = os.environ.get('STU_AFFIL_QUERY')
    student_affil = pd.read_sql(con=informix, sql=query)
    all_students = pd.merge(aamc_found, student_affil, on='entity_id', how='left')
    all_students = all_students.fillna('None')
    stu_affil = all_students[(all_students.category_code=='STU-AFFIL ')]
    aamc_found = all_students[(all_students.category_code!='STU-AFFIL ')]
    return aamc_found, stu_affil

def fix_id(num):
    num = str(num).strip().replace('.0', '')
    num = ''.join(filter(str.isdigit, num))
    if len(num) == 4:
        num = '0' + num
    elif len(num) == 3:
        num = '00' + num
    elif len(num) == 2:
        num = '000' + num
    elif len(num) == 1:
        num = '0000' + num
    return num

#add info
def add_details(aamc_found, all_students, me_entity):
    found_info = pd.merge(aamc_found, all_students, on='entity_id')
    found_info = found_info.fillna('None')
    school_crosswalk_file = os.environ.get('SCHOOL_CROSSWALK')
    school_crosswalk = pd.read_excel(school_crosswalk_file)
    status_crosswalk_file = os.environ.get('STATUS_CROSSWALK')
    status_crosswalk = pd.read_excel(status_crosswalk_file)
    found_students = pd.merge(found_info , status_crosswalk, left_on='Curr Status', right_on='STATUS_DESC', how='left')
    found_students  = pd.merge(found_students , school_crosswalk, on='INST_ID', how='left')
    found_students['AMA_ID'] = [fix_id(x) for x in found_students.AMA_ID]
    found_students = pd.merge(found_students, me_entity, on='entity_id', how='left')
    found_students['ama_status'] = found_students['AMA Status']
    founded = found_students[found_students['Curr Exp Grad Date']!='None']
    unfounded = found_students[found_students['Curr Exp Grad Date']=='None']
    founded['CURRENT_GRAD_YEAR'] = [x.year for x in pd.to_datetime(founded['Curr Exp Grad Date'])]
    unfounded['CURRENT_GRAD_YEAR'] = 'None'
    found_students = pd.concat([founded, unfounded]).drop_duplicates()
    return found_students

#grad_year
def find_grad_year_updates(found_students):
    founded = found_students[found_students['Curr Exp Grad Date']!='None']
    unfounded = found_students[found_students['Curr Exp Grad Date']=='None']
    founded['CURRENT_GRAD_YEAR'] = [x.year for x in pd.to_datetime(founded['Curr Exp Grad Date'])]
    unfounded['CURRENT_GRAD_YEAR'] = 'None'
    found_students = pd.concat([founded, unfounded])
    grad_match = []
    for row in found_students.itertuples():
        if row.CURRENT_GRAD_YEAR != row.grad_yr:
            grad_match.append(False)
        else:
            grad_match.append(True)
    found_students['grad_match'] = grad_match
    grad_mismatch = found_students[found_students.grad_match == False]
    return grad_mismatch
    
#status
def find_status_updates(found_students, grad_year):
    status_match = []
    for row in found_students.itertuples():
        if row.ama_status != row.edu_sts:
            status_match.append(False)
        else:
            status_match.append(True)
    found_students['status_match'] = status_match
    status_mismatch = found_students[found_students.status_match == False]
    status_update = status_mismatch[status_mismatch.aamc_id.isin(grad_year.aamc_id)==False]
    return status_update

def process(grad_year, status_update):
    processing_rules_file = os.environ.get('PROCESSING_RULES')
    processing_rules = pd.read_excel(processing_rules_file)
    stats = pd.merge(processing_rules, status_update, left_on = ['Curr Status', 'edu_status'], right_on =['Curr Status', 'edu_sts'])
    manual = stats[(stats['PROCESS?']=='N')&(stats['NEW EDU_STS/ACTION']=='Flag for Manual Review')]
    auto = stats[(stats['PROCESS?']=='Y')][['aamc_id','NEW EDU_STS/ACTION','NEW STS REASON','NEW CATEGORY CODE','Curr Status Date','Curr Exp Grad Date']]
    other_sts = status_update[status_update.aamc_id.isin(stats.aamc_id)==False]
    manual = pd.concat([manual, other_sts])
    unprocessed = stats[(stats['PROCESS?']=='N')&(stats['NEW EDU_STS/ACTION']!='Flag for Manual Review')]
    return manual, auto, unprocessed

def get_columns():
    column_dict = {
        'MATCHED': ['me','aamc_id',
                    'entity_id',
                    'school_id',
                    'stud_id', 'Date of Birth',
                    'birth_dt',
                    'Name',
                    'first_nm',
                    'middle_nm',
                    'last_nm',
                    'gender',
                    'Sex', 'Birth State', 'birth_state_cd',
                    'grad_yr',
                    'degree_cd',
                    'Current Degree Program',
                    'Curr Class Level',
                    'Curr Exp Grad Date',
                    'Curr Med School Campus',
                    'Curr Status',
                    'Curr Status AcadYear',
                    'Curr Status Date'
                    ],
        'STATUS_UPDATE': ['me','aamc_id',
                        'stud_id',
                        'grad_yr',
                        'CURRENT_GRAD_YEAR',
                        'school_id',
                        'edu_sts',
                        'edu_pref_cd',
                        'degree_cd',
                        'STATUS_CD',
                        'STATUS_DESC',
                        'STATUS_LBL',
                        'ama_status',
                        'AMA Status Reason',
                        'AMA Rule',
                        'INST_TYPE_CD',
                        'INST_NAME_120',
                        'AMA_ID',
                        'Birth Country',
                        'Birth County',
                        'Birth State',
                        'Citizen Country',
                        'Curr Class Level',
                        'Curr Class Level Eff Date',
                        'Curr Exp Grad Date',
                        'Curr Med School Campus',
                        'Curr Status',
                        'Curr Status AcadYear',
                        'Curr Status Date',
                        'Current Degree Program',
                        'Date of Birth',
                        'Email',
                        'INST_ID',
                        'Legal Country',
                        'Legal County',
                        'Legal State',
                        'Matriculation Degree Program',
                        'Name',
                        'Preferred USMLE ID',
                        'RaceEthnicity',
                        'Sex',
                        'Visa Desc'],
        'GRAD_YEAR': ['me','aamc_id',
                    'stud_id',
                    'grad_yr',
                    'CURRENT_GRAD_YEAR',
                    'school_id',
                    'edu_sts',
                    'edu_pref_cd',
                    'degree_cd',
                    'STATUS_CD',
                    'STATUS_DESC',
                    'STATUS_LBL',
                    'AMA Status',
                    'AMA Status Reason',
                    'AMA Rule',
                    'INST_TYPE_CD',
                    'INST_NAME_120',
                    'AMA_ID',
                    'Birth Country',
                    'Birth County',
                    'Birth State',
                    'Citizen Country',
                    'Curr Class Level',
                    'Curr Class Level Eff Date',
                    'Curr Exp Grad Date',
                    'Curr Med School Campus',
                    'Curr Status',
                    'Curr Status AcadYear',
                    'Curr Status Date',
                    'Current Degree Program',
                    'Date of Birth',
                    'Email',
                    'INST_ID',
                    'Legal Country',
                    'Legal County',
                    'Legal State',
                    'Matriculation Degree Program',
                    'Name',
                    'Preferred USMLE ID',
                    'RaceEthnicity',
                    'Sex',
                    'Visa Desc'],
        'MISSING': ['aamc_id',
                    'Birth Country',
                    'Birth County',
                    'Birth State',
                    'Citizen Country',
                    'Curr Class Level',
                    'Curr Class Level Eff Date',
                    'Curr Exp Grad Date',
                    'Curr Med School Campus',
                    'Curr Status',
                    'Curr Status AcadYear',
                    'Curr Status Date',
                    'Current Degree Program',
                    'Date of Birth',
                    'Email',
                    'Legal Country',
                    'Legal County',
                    'Legal State',
                    'Matriculation Degree Program',
                    'Name',
                    'Preferred USMLE ID',
                    'RaceEthnicity',
                    'Sex',
                    'Visa Desc']
    }
    return column_dict

def get_me_entity_map():
    LOGGER.info("Getting ME numbers...")
    informix = aims_connect()
    query = os.environ.get('ME_ENTITY_QUERY')
    me_entity = pd.read_sql(con=informix, sql=query)

    return me_entity

def clean(data, type):
    column_dict = get_columns()
    data = data[column_dict[type]].drop_duplicates()
    return data

def fix_me(me_number):
    num = str(me_number)
    num = num.replace('.0', '')
    if len(num) == 10:
        num = '0' + num
    elif len(num) == 9:
        num = '00' + num
    elif len(num) == 8:
        num = '000' + num
    return num

def whole_shebang():
    today = str(date.today())
    out = os.environ.get('OUT_DIR')
    srs_old = get_old_scrape()
    srs_old = pd.read_csv(f'{out}/SRS_Scrape_2021-03-19.csv')
    LOGGER.info("Scraping...")
    srs_new = scrape_srs()
    srs_new = pd.read_csv(f'{out}/SRS_Scrape_2021-07-27.csv')
    LOGGER.info(f'{"{:,}".format(len(srs_new))} student records in AAMC-SRS scrape')
    updates = find_updates(srs_old, srs_new)
    LOGGER.info(f'{"{:,}".format(len(updates))} record updates since last scrape')
    LOGGER.info("Finding in masterfile...")
    aamc_found, missing = match_aamc(updates)
    aamc_found_all, missing_all = match_aamc(srs_new)

    # aamc_found = pd.read_csv(f'{out}/SRS_AAMC_{today}.csv')
    # missing = pd.read_csv(f'{out}/SRS_AAMC_Missing_{today}.csv') 

    LOGGER.info(f'{"{:,}".format(len(aamc_found))} ({round(len(aamc_found)/len(updates)*100, 2)}%) records matched to AIMS on aamc_id')
    aamc_found, stu_affil = get_stu_affil(aamc_found)
    LOGGER.info(f'{"{:,}".format(len(stu_affil))} ({round(len(stu_affil)/len(aamc_found)*100, 2)}%) records are student affiliates')
    LOGGER.info("Getting all student data...")
    all_students = get_all_students()
    # all_students = pd.read_csv(f'{out}/all_students_{today}.csv')
    LOGGER.info("Matching...")
    matched = match_missing_ids(missing, all_students)
    # matched = pd.read_csv(f'{out}/matched_{today}.csv')
    matched = pd.merge(matched, missing, on='AAMC ID')
    matched = pd.merge(matched, all_students, on='entity_id')
    me_entity = get_me_entity_map()
    # me_entity = pd.read_csv(f'{out}/me_entity_{today}.csv')
    matched = pd.merge(matched, me_entity, on='entity_id', how='left')
    
    still_missing = missing[missing['AAMC ID'].isin(matched['AAMC ID'])==False]
    LOGGER.info(f'{"{:,}".format(len(matched))} ({round(len(matched)/len(missing)*100, 2)}%) records found via matching process')
    LOGGER.info(f'{"{:,}".format(len(still_missing))} ({round(len(still_missing)/len(missing)*100, 2)}%) scraped records missing from our database')
    LOGGER.info('Adding infos...')
    found_students = add_details(aamc_found, all_students, me_entity)
    LOGGER.info('Processing discrepancies...')
    grad_mismatch = clean(find_grad_year_updates(found_students), 'GRAD_YEAR')
    LOGGER.info(f'{"{:,}".format(len(grad_mismatch))} ({round(len(grad_mismatch)/len(found_students)*100, 2)}%) records have graduation year discrepancies')
    status_update = clean(find_status_updates(found_students, grad_mismatch), 'STATUS_UPDATE')
    LOGGER.info(f'{"{:,}".format(len(status_update))} ({round(len(status_update)/len(found_students)*100, 2)}%) records have status discrepancies, but correct graduation year')
    manual, auto, unprocessed = process(grad_mismatch, status_update)
    LOGGER.info(f'{"{:,}".format(len(manual))} status discrepancies flagged for manual review')
    LOGGER.info(f'{"{:,}".format(len(auto))} status discrepancies automatically processed')
    LOGGER.info(f'{"{:,}".format(len(unprocessed))} status discrepancies not processed')
    updates.to_csv(f'{out}/SRS_Scraped_New_{today}.csv', index=False)
    found_students.to_csv(f'{out}/SRS_AAMC_{today}.csv', index=False)
    aamc_found_all.to_csv(f'{out}/SRS_AAMC_All_{today}.csv', index=False)
    clean(matched, 'MATCHED').to_csv(f'{out}/SRS_Matched_{today}.csv', index=False)
    clean(still_missing, 'MISSING').to_csv(f'{out}/SRS_Missing_{today}.csv', index=False)
    grad_mismatch.to_csv(f'{out}/SRS_Graduation_Year_Discrepancy_{today}.csv', index=False)
    status_update.to_csv(f'{out}/SRS_Status_Discrepancy_{today}.csv', index=False)
    stu_affil.to_csv(f'{out}/SRS_Student_Affiliates_{today}.csv', index=False)
    auto.to_csv(f'{out}/Automatic_Updates_{today}.csv', index=False)
    manual.to_csv(f'{out}/SRS_Manual_Updates_{today}.csv', index=False)
    unprocessed.to_csv(f'{out}/SRS_Unprocessed_{today}.csv', index=False)

if __name__ == "__main__":
    whole_shebang()