from datetime import date
import pandas as pd
import settings
import os
import json
from   enum import Enum
from datalabs.access.edw import EDW, PartyKeyType
from fuzzywuzzy import fuzz
import logging

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def get_newest(path_text, text):
    '''Get newest filename'''
    path = os.environ.get(path_text)
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if text in basename]
    LOGGER.info(f'Reading {text} file in {path}')
    dataframe = pd.read_csv(max(paths, key=os.path.getctime))
    return dataframe

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

def get_humach_results(): 
    humach = get_newest('HUMACH_FOLDER', 'humach_updated')
    humach = humach.fillna('None')
    humach['ME'] = fix_me(humach.PHYSICIAN_ME_NUMBER)
    return humach

def get_key_table():
    LOGGER.info('Getting key tables')
    with EDW() as edw:
        entity_to_party = edw.get_party_keys_by_type(PartyKeyType.ENTITY)
        me_to_party = edw.get_party_keys_by_type(PartyKeyType.ME)
    key_table = pd.merge(entity_to_party, me_to_party, on='PARTY_ID')
    return key_table

def get_addresses():
    LOGGER.info('Getting POLO and PPMA addresses')
    with EDW() as edw:
        LOGGER.info('Getting PPMA addresses')
        ppma = edw.read(os.environ.get('PPMA_QUERY'))
        LOGGER.info('Getting POLO addresses')
        polo = edw.read(os.environ.get('POLO_QUERY'))
    addresses = pd.merge(polo, ppma, on='PARTY_ID', suffixes = ['_POLO','_PPMA'])
    addresses = addresses.fillna('None')
    return addresses

def get_ppd():
    key_table = get_key_table()
    ppd = get_newest('PPD_FOLDER', 'ppd')
    LOGGER.info('Cleaning PPD')
    ppd['ME']=fix_me(ppd.ME)
    ppd = ppd.fillna('None')
    ppd = pd.merge(ppd, key_table, on = 'ME')
    return ppd

def filter_polos():
    addresses = get_addresses()
    ppd = get_ppd()
    LOGGER.info('Finding filtered POLOs')
    no_polo = ppd[(ppd.POLO_MAILING_LINE_1=='None')&(ppd.POLO_MAILING_LINE_2=='None')]
    filtered_polos = pd.merge(no_polo, addresses, on='PARTY_ID')
    LOGGER.info(f'{len(filtered_polos)} filtered out of PPD')
    filtered_dpc = filtered_polos[filtered_polos.TOP_CD == 20]
    LOGGER.info(f'{len(filtered_dpc)} DPC POLOs filtered out of PPD')
    return filtered_dpc

def find_newer_polos(filtered_dpc):
    LOGGER.info('Finding newer filtered POLOs')
    newers = []
    for row in filtered_dpc.itertuples():
        newer = False
        if row.FROM_DT_POLO > row.FROM_DT_PPMA:
            newer = True
        newers.append(newer)
    filtered_dpc['POLO_NEWER'] = newers
    newer_dpc = filtered_dpc[filtered_dpc.POLO_NEWER==True]
    LOGGER.info(f'{len(newer_dpc)} filtered DPC POLOs are newer than their PPMAs')
    return newer_dpc
      
def add_humach_results(newer_dpc):
    humach =  get_humach_results()
    newer_dpc = newer_dpc.fillna('None')
    newer_dpc['ME']=fix_me(newer_dpc.ME)
    newer_dpc['OFFICE_ADDRESS_LINE_2'] = [x.upper().replace('.','') for x in newer_dpc.ADDR_1_POLO]
    dpc_with_humach = pd.merge(newer_dpc, humach, right_on = ['ME','OFFICE_ADDRESS_STATE'], left_on=['ME','STATE_POLO'], suffixes = ['_POLO','_HUMACH'])
    return dpc_with_humach
    
def check_match(thing_1, thing_2):
    '''match check'''
    if thing_1 == thing_2:
        return True
    elif thing_1 in thing_2 or thing_2 in thing_1:
        return True
    elif fuzz.ratio(thing_1, thing_2) > 60:
        return True
    else:
        return False

def find_humach_matches(newer_dpc):
    LOGGER.info('Finding recently validated')
    dpc_with_humach = add_humach_results(newer_dpc)
    corrects =[]
    for row in dpc_with_humach.itertuples():
        one = row.OFFICE_ADDRESS_LINE_2_HUMACH
        two = row.OFFICE_ADDRESS_LINE_2_POLO
        correct =  check_match(one,two)
        corrects.append(correct)
    dpc_with_humach['ADDRESS_VALIDATED'] = corrects
    validated = dpc_with_humach[dpc_with_humach.ADDRESS_VALIDATED==True]
    validated = validated.drop_duplicates('ME')
    LOGGER.info(f'{len(validated)} newer filtered DPC POLOs have been recently validated by Humach')
    return validated

def get_license():
    LOGGER.info('Getting state license info')
    with EDW() as edw:
        license = edw.read(os.environ.get('LICENSE_QUERY'))
    return license

def concatenate_licenses(newer_validated_dpc):
    license = get_license()
    dpc_with_license = pd.merge(newer_validated_dpc, license, on='PARTY_ID', suffixes = ['_PPD',''])
    license_dictionary = {}
    for row in dpc_with_license.itertuples():
        if row.ME in license_dictionary.keys():
            license_dictionary[row.ME].append(row.STATE_CD)
        else:
            license_dictionary[row.ME] = [row.STATE_CD]
    return license_dictionary

def find_license_matches(newer_validated_dpc):
    license_dictionary = concatenate_licenses(newer_validated_dpc)
    matching_licenses = []
    for row in newer_validated_dpc.itertuples():
        if row.ME not in license_dictionary.keys():
            keep = False
        elif row.ADDRESS_TYPE == '1.0' and row.STATE_POLO in license_dictionary[row.ME]:
            keep = True
        elif row.STATE_POLO in license_dictionary[row.ME] and row.STATE_PPMA not in license_dictionary[row.ME]:
            keep = True
        else:
            keep = False
        matching_licenses.append(keep)
    newer_validated_dpc['LICENSE_MATCH'] = matching_licenses
    matched_license = newer_validated_dpc[newer_validated_dpc.LICENSE_MATCH == True]
    LOGGER.info(f'{len(matched_license)} filtered POLOs meet all business requirements')
    return matched_license

def get_col():
    '''Get column dict'''
    columns = {
        'ME':'me#',
        'COMM_ID':'comm_id',
        'ADDR_1_POLO':'addr_line_1',
        'ADDR_2_POLO':'addr_line_2',
        'ADDR_3_POLO':'addr_line_3',
        'CITY_POLO':'addr_city',
        'STATE_POLO':'addr_state',
        'ZIP_POLO':'addr_zip'}
    return columns

def clean_file(all_that, today):
    '''Clean and format data'''
    LOGGER.info('Cleaning file')
    all_that = all_that.drop_duplicates(['ME'])
    all_that['ADDR_2_POLO'] = ['' if x=='None' else x for x in all_that.ADDR_2_POLO]
    all_that['ADDR_3_POLO'] = ['' if x=='None' else x for x in all_that.ADDR_3_POLO]
    all_that['usage'] = 'PP'
    all_that['load_type_ind'] = 'R'
    all_that['addr_type'] = 'OF'
    all_that['source'] = 'POLO-PPD'
    all_that['source_dtm'] = today
    col = get_col()
    all_that = all_that[['ME',
                         'COMM_ID',
                         'usage',
                         'load_type_ind',
                         'addr_type',
                         'ADDR_1_POLO',
                         'ADDR_2_POLO',
                         'ADDR_3_POLO',
                         'CITY_POLO',
                         'STATE_POLO',
                         'ZIP_POLO',
                         'source',
                         'source_dtm',
                         ]].rename(columns=col)
    return all_that

def create_and_save_file():
    u_output = os.environ.get('UDRIVE_FOLDER')
    local_output = os.environ.get('LOCAL_FOLDER')
    today = str(date.today())
    
    filtered_polos = filter_polos()
    filtered_polos.to_csv(f'{local_output}/Filtered_POLOs_{today}.csv', index=False)
    newer_filtered = find_newer_polos(filtered_polos)
    newer_filtered.to_csv(f'{local_output}/Newer_Filtered_POLOs_{today}.csv', index=False)
    filtered_polos[filtered_polos.ME.isin(newer_filtered.ME==False)].to_csv(f'{local_output}/Older_Filtered_POLOs_{today}.csv', index=False)
    # newer_filtered = pd.read_csv(f'{local_output}/Newer_Filtered_POLOs_2021-05-28.csv')
    validated_newer_filtered = find_humach_matches(newer_filtered)
    # validated_newer_filtered = pd.read_csv(f'{local_output}/Recently_Validated_2021-05-28.csv')
    validated_newer_filtered.to_csv(f'{local_output}/Recently_Validated_{today}.csv', index=False)
    acceptable_updates = find_license_matches(validated_newer_filtered)
    
    cleaned_file = clean_file(acceptable_updates, today)
    cleaned_file.to_csv(f'{u_output}/address_load.csv', index=False)
    cleaned_file.to_csv(f'{local_output}/address_load_{today}.csv', index=False)

if __name__ == "__main__":
    create_and_save_file()


