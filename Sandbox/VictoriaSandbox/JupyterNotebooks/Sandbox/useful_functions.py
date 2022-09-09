import pandas as pd
import pyodbc
import os
import logging

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def get_columns():
    cols = [
        'ME',
        'RECORD_ID',
        'UPDATE_TYPE',
        'ADDRESS_TYPE',
        'MAILING_NAME',
        'LAST_NAME',
        'FIRST_NAME',
        'MIDDLE_NAME',
        'SUFFIX',
        'MAILING_LINE_1',
        'MAILING_LINE_2',
        'CITY',
        'STATE',
        'ZIP',
        'SECTOR',
        'CARRIER_ROUTE',
        'ADDRESS_UNDELIVERABLE_FLAG',
        'FIPS_COUNTY',
        'FIPS_STATE',
        'PRINTER_CONTROL_CODE',
        'PC_ZIP',
        'PC_SECTOR',
        'DELIVERY_POINT_CODE',
        'CHECK_DIGIT',
        'PRINTER_CONTROL_CODE_2',
        'REGION',
        'DIVISION',
        'GROUP',
        'TRACT',
        'SUFFIX_CENSUS',
        'BLOCK_GROUP',
        'MSA_POPULATION_SIZE',
        'MICRO_METRO_IND',
        'CBSA',
        'CBSA_DIV_IND',
        'MD_DO_CODE',
        'BIRTH_YEAR',
        'BIRTH_CITY',
        'BIRTH_STATE',
        'BIRTH_COUNTRY',
        'GENDER',
        'TELEPHONE_NUMBER',
        'PRESUMED_DEAD_FLAG',
        'FAX_NUMBER',
        'TOP_CD',
        'PE_CD',
        'PRIM_SPEC_CD',
        'SEC_SPEC_CD',
        'MPA_CD',
        'PRA_RECIPIENT',
        'PRA_EXP_DT',
        'GME_CONF_FLG',
        'FROM_DT',
        'TO_DT',
        'YEAR_IN_PROGRAM',
        'POST_GRADUATE_YEAR',
        'GME_SPEC_1',
        'GME_SPEC_2',
        'TRAINING_TYPE',
        'GME_INST_STATE',
        'GME_INST_ID',
        'MEDSCHOOL_STATE',
        'MEDSCHOOL_ID',
        'MEDSCHOOL_GRAD_YEAR',
        'NO_CONTACT_IND',
        'NO_WEB_FLAG',
        'PDRP_FLAG',
        'PDRP_START_DT',
        'POLO_MAILING_LINE_1',
        'POLO_MAILING_LINE_2',
        'POLO_CITY',
        'POLO_STATE',
        'POLO_ZIP',
        'POLO_SECTOR',
        'POLO_CARRIER_ROUTE',
        'MOST_RECENT_FORMER_LAST_NAME',
        'MOST_RECENT_FORMER_MIDDLE_NAME',
        'MOST_RECENT_FORMER_FIRST_NAME',
        'NEXT_MOST_RECENT_FORMER_LAST',
        'NEXT_MOST_RECENT_FORMER_MIDDLE',
        'NEXT_MOST_RECENT_FORMER_FIRST'
    ]
    return cols

def get_newest_ppd():
    local_ppd_folder = 'C:/Users/vigrose/Data/PPD'
    previous_ppd_file = get_newest(local_ppd_folder, 'ppd_data')
    u_ppd_folder = "U:/Source Files/Data Analytics/Baseline/data/"
    current_ppd_file = get_newest(u_ppd_folder, 'PhysicianProfessionalDataFile')
    previous_ppd_date = pd.to_datetime(previous_ppd_file.split('_')[-1].replace('.csv',''))
    current_ppd_date = pd.to_datetime(current_ppd_file.split('_')[1])
    if previous_ppd_date < current_ppd_date :
        LOGGER.info(f'Newest ppd is from {current_ppd_date.strftime("%b" " " "%d" " " "%Y")}')
        ppd = create_ppd_csv(current_ppd_file)
    else:
        LOGGER.info(f'PPD file has not been updated since {previous_ppd_date.strftime("%b" " " "%d" " " "%Y")}')
        ppd = get_local_ppd()
    return ppd

def get_local_ppd():
    ppd_loc = 'C:/Users/vigrose/Data/PPD'
    ppd_file = get_newest(ppd_loc, 'ppd')
    updated = pd.to_datetime(ppd_file.split('_')[-1].replace('.csv','')).strftime("%b" " " "%d" " " "%Y")
    LOGGER.info(f'Reading local ppd from {updated}')
    ppd = pd.read_csv(ppd_file)
    ppd['ME'] = fix_me(list(ppd['ME']))
    return ppd

def create_ppd_csv(current_ppd_file):
    ppd_date = pd.to_datetime(current_ppd_file.split('_')[1]).strftime("%Y%m%d")
    local_folder = "C:/Users/vigrose/Data/PPD"
    cols = get_columns()
    LOGGER.info('Getting PPD data from UDrive...')
    ppd = pd.read_csv(current_ppd_file, names=cols, sep='|', encoding='IBM437', index_col=False, dtype=object)
    ppd_file =  f'{local_folder}/ppd_data_{ppd_date}.csv'
    LOGGER.info('Saving PPD as csv in ppd folder...')
    ppd.to_csv(ppd_file, header=True, index=False)
    ppd['ME'] = fix_me(list(ppd['ME']))
    return ppd
                    
def get_npi_to_me():
    username = 'vigrose'
    password_edw = 'Hufflepuff~10946'

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

def get_entity_to_me():
    username = 'vigrose'
    password_edw = 'Ravenclaw~10946'

    QUERY = \
        """
        SELECT DISTINCT 
        M.ME, E.ENTITY_ID 
        FROM 
        AMAEDW.PARTY_ID_TO_ME_VW M, AMAEDW.PARTY_ENTITY_VW E 
        WHERE 
        M.PARTY_ID=E.PARTY_ID
        """
    #Execute queries
    w = "DSN=PRDDW; UID={}; PWD={}".format(username, password_edw)
    AMAEDW = pyodbc.connect(w)
    ENTITY_TO_ME = pd.read_sql(con=AMAEDW, sql=QUERY)

    return ENTITY_TO_ME


def get_newest(path, text):
    '''Get newest filename'''
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if text in basename]
    return max(paths, key=os.path.getctime)

def fix_zipcode(num):
    num = str(num).strip().replace('.0', '')
    num = ''.join(filter(str.isdigit, num))
    if len(num) > 5:
        num = num[:-4]
    if len(num) == 4:
        num = '0' + num
    elif len(num) == 3:
        num = '00' + num
    elif len(num) == 2:
        num = '000' + num
    return num
    
def fix_me(me_list):
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

def fix_phone(num):
    num = str(num).strip().replace('.0', '')
    if num[0] == '1':
        num = num[1:]
    num = ''.join(filter(str.isdigit, num))
    num = num[:10]
    return num