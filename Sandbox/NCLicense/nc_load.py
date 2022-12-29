import pandas as pd
import settings
import os
from datetime import date
import logging
import numpy as np

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def find_all_scraped_data():
    out_dir = os.environ.get('LICENSE_DIR')
    this_month = date.today().strftime("%Y-%m")
    # this_month = '2021-11'
    file_list = []
    for file in os.listdir(out_dir):
        if file.startswith(f"NC_License_Status_{this_month}"):
            file_list.append(f'{out_dir}{file}')
    return file_list

def find_og_file():
    this_month = date.today().strftime("%Y-%m")
    out_dir = os.environ.get('LICENSE_DIR')
    for file in os.listdir(out_dir):
        if file.startswith(f"NC_{this_month}"):
            og_file = (f'{out_dir}{file}')
            break
    return og_file

def concat_scraped_data(file_list):
    df_list = []
    for file in file_list:
        df_list.append(pd.read_csv(file))
    all_scraped_data = pd.concat(df_list).drop_duplicates('License_Number')
    print(len(all_scraped_data))
    return all_scraped_data

def confirm_completeness(all_scraped_data, og_file):
    missing = og_file[og_file.License_Number.isin(all_scraped_data.License_Number)==False]
    if len(missing)>0:
        status = False
    else:
        status = True
    return status

def public_flag_update(data):
    types = ['DO Faculty Limited/WFU & Affiliated Institutions',
            'DO Limited Emergency License',
            'DO Retired Limited Volunteer',
            'MD Faculty Limited',
            'MD Faculty Limited/Duke & Affiliated Institutions',
            'MD Faculty Limited/ECU & Affiliated Institutions',
            'MD Faculty Limited/UNC & Affiliated Institutions',
            'MD Faculty Limited/WFU & Affiliated Institutions',
            'MD Faculty Limited/Duke/UNC & Affiliated Institutions', 
            'MD Limited Emergency License',
            'MD Limited License Volunteer',
            'MD Retired Limited Volunteer',
            'MD Special Permit License',
            'MD Special Volunteer',
            'MD Volunteer Limited',
            'MD Special Purpose License']
    for lic_type in data.License_Type.unique():
        split_type = lic_type.split(' ')
        if len(split_type)>1 and split_type[0] in ['MD','DO']:
            if lic_type not in types:
                LOGGER.info(f'New License Type parameter added: {lic_type}')
                types.append(lic_type)
    data['PublicFlag'] = ['Y' if x in types else np.NaN for x in data.License_Type]
    data = data.rename(columns={'License_Type':'License_Type_Website'})
    return data

def sanity_check(old, new):
    diff = abs(old - new) < 0.05*old
    return diff
    
def check_data(data_new):
    new_length = len(data_new)
    LOGGER.info(f'{new_length} total records')
    new_public = data_new.PublicFlag.count()
    LOGGER.info(f'{new_public} public flag records')
    old_length = 42804
    old_public = 830
    check = False
    if sanity_check(old_length, new_length) and sanity_check(old_public, new_public):
        check = True
    return check

def create_file():
    today = str(date.today())
    this_month = date.today().strftime("%B")
    LOGGER.info('Finding scraped data...')
    file_list = find_all_scraped_data()
    LOGGER.info('Concatenating scraped data...')
    all_scraped_data = concat_scraped_data(file_list)
    local_out = os.environ.get('LICENSE_DIR')
    u_out = os.environ.get('RAW_LICENSE_DIR')
    local_file = f'{local_out}NC_License_Status_{today}.csv'
    u_file = f'{u_out}{this_month}/License/North Carolina/MD Active Type Fixed.txt'
    # u_file = f'{local_out}MD Active Type Fixed.txt'
    LOGGER.info('Reading original file...')
    og_filename = find_og_file()
    og_file = pd.read_csv(og_filename)
    missing = og_file[og_file.License_Number.isin(all_scraped_data.License_Number)==False]
    print(len(missing))
    if confirm_completeness(all_scraped_data, og_file):
        LOGGER.info('Updating...')
        all_scraped_data = public_flag_update(all_scraped_data)
        confirm = check_data(all_scraped_data)
        LOGGER.info(f'Data length consistent with previously loaded file: {confirm}')
        LOGGER.info('Merging...')
        data = pd.merge(og_file, all_scraped_data, suffixes = ['OLD',''], on='License_Number').drop_duplicates()
        LOGGER.info('Saving to UDrive...')
        data['Medical_School_Graduation_Year'] = [str(x).replace('.0','') for x in data.Medical_School_Graduation_Year]
        data[og_file.columns].to_csv(u_file, sep = '\t', index=False)
        LOGGER.info('Saving locally...')
        data[og_file.columns].to_csv(local_file, index=False)
    else:
        LOGGER.error('Scraping was incomplete')

if __name__ == "__main__":
    create_file()
