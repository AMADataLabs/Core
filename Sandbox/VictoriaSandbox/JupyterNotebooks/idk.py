import pandas as pd 
import useful_functions as use


#humach file

#data load

humach_columns = [['ME',
 'FIRST_NAME',
 'MIDDLE_NAME',
 'LAST_NAME',
 'SUFFIX',
 'POLO_MAILING_LINE_1',
 'POLO_MAILING_LINE_2',
 'POLO_CITY',
 'POLO_STATE',
 'POLO_ZIP',
 'TELEPHONE_NUMBER',
 'PRIM_SPEC_CD',
 'DESCRIPTION',
 'PE_CD',
 'FAX_NUMBER']]

 use.fix_me()

 use.fix_zip

def add_pe_description(data):
    ppd_folder = os.environ.get('PPD_FOLDER')
    pe_cd_filename = use.get_newest('PRESENT_EMPLOYMENT', ppd_folder)
    pe_codes = pd.read_excel(pe_cd_filename)
    data = pd.merge(data, pe_codes, left_on = , right_on = 'present_emp_cd')
    return data

def add_ppd(data):
    ppd = use.get_ppd()
    data = pd.merge(data, ppd, on = 'ME')
    return data


def add_loading_info(source, results):
    if source = 'CRED-ADDR':
        results['load_type_ind'] = 'A'
        results['addr_type'] = 'OF'
    elif source = 'INS-USG':
        results['usage'] = 'PP'
        results['load_type_ind'] = 'R'
        results['addr_type'] = 'N'
    elif source = 'POLO-PPD':
        all_that['usage'] = 'PP'
        all_that['load_type_ind'] = 'R'
        all_that['addr_type'] = 'OF'
    else:
        results['load_type_ind'] = 'A'
        results['addr_type'] = 'N'
    results['source'] = source
    return results

def clean_columns(data):
    data.columns 

def create_address_columns(data):
    for col in data.columns:
        if 'ZIP' in col:
            data['ZIPCODE'] = [use.fix_zip(x) for z in data.col]
        elif 'STATE' in col:
        elif 'CITY' in col:
        elif 'PHONE' in col:
        elif 'ADDR' in col:
            if '1' in col:
            if '2' in col: