# Kari Palmier    8/30/19    Created
#
#############################################################################
import datetime
import os
import sys
import tkinter as tk
from tkinter import filedialog

import pandas as pd

import logging

import settings
from get_aims_db_tables import get_no_contacts, get_active_licenses, get_ent_comm_phones
from get_aims_db_tables import get_spec_description, get_entity_me_key

from datalabs.access.aims import AIMS
from datalabs.access.edw import EDW
import datalabs.curate.dataframe  # pylint: disable=unused-import


# Gets historical phone numbers for a list of given physicians, specified by entity ids
def get_old_phones(uniq_ent_comm_df, uniq_ent_ids):
    
    max_num_phones = 0
    temp_phone_dict = {}
    for i in range(len(uniq_ent_ids)):
        temp_df = uniq_ent_comm_df[uniq_ent_comm_df['entity_id'] == uniq_ent_ids[i]]
        temp_phones = list(temp_df['aims_phone'])
        
        num_phones = len(temp_phones)
        
        if num_phones > max_num_phones:
            max_num_phones = num_phones
        
        temp_phone_dict[uniq_ent_ids[i]] = {}
        temp_phone_dict[uniq_ent_ids[i]]['num_phones'] = len(temp_phones)
        temp_phone_dict[uniq_ent_ids[i]]['old_phones'] = temp_phones
        
    old_phone_df = pd.DataFrame({'entity_id':uniq_ent_ids})
    for i in range(max_num_phones):
        
        name = 'oldphone' + str((i + 1))
        old_phone_df[name] = ''
    
    for ent_key in temp_phone_dict.keys():
        
        num_phones = temp_phone_dict[ent_key]['num_phones']
        phone_list = temp_phone_dict[ent_key]['old_phones']
        
        ent_id_ndx = old_phone_df[old_phone_df['entity_id'] == ent_key].index[0]
        
        for i in range(len(phone_list)):
            
            phone = phone_list[i]
            name = 'oldphone' + str(i + 1)
            old_phone_df.loc[ent_id_ndx, name] = phone
            
    oldphone_name_list = ['oldphone' + str(i + 1) for i in range(max_num_phones)]
            
    return old_phone_df, oldphone_name_list


base_vt_batch_cols = ['LAST_NAME', 'FIRST_NAME', 'MIDDLE_NAME', 'MEDSCHOOL_GRAD_YEAR',
                      'MEDSCHOOL_NAME', 'degree_type', 'specialty', 'POLO_CITY',
                      'POLO_STATE', 'POLO_ZIP', 'lic_state', 'lic_nbr']

root = tk.Tk()
root.withdraw()

# Get files needed
ddb_info_file = filedialog.askopenfilename(initialdir="C:\\",
                                           title="Choose txt file with database login information...")

# Get model file needed
ppd_file = filedialog.askopenfilename(initialdir="U:\\Source Files\\Data Analytics\\Data-Science\\Data\\PPD\\",
                                      title="Choose the latest PPD file...")

init_save_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Vertical_Trail\\Batches_To_VT\\'
out_dir = filedialog.askdirectory(initialdir=init_save_dir, title="Choose directory to save sample in...")
out_dir = out_dir.replace("/", "\\")
out_dir += "\\"

batch_str = input('Enter the batch size: ')
if not(batch_str.isnumeric()):
    print('Invalid batch size.')
    sys.exit()

batch_size = int(batch_str)

current_time = datetime.datetime.now()
start_time_str = current_time.strftime("%Y-%m-%d")

phone_var_name = 'TELEPHONE_NUMBER'

logging.info('STARTING')
logging.info('PULLING DATA - EDW')
with EDW() as edw:
    party_key_df = edw.get_school_ids()
    act_grad_name_df = edw.get_active_medical_school_map()

logging.info('PULLING DATA - AIMS')
with AIMS() as aims:
    entity_key_df = get_entity_me_key(aims._connection)
    entity_comm_me_df = get_ent_comm_phones(aims._connection)
    no_contact_df = get_no_contacts(aims._connection)
    active_license_df = get_active_licenses(aims._connection)
    spec_desc_df = get_spec_description(aims._connection)

logging.info('PULLING DATA - PPD')
ppd_df = pd.read_csv(ppd_file, delimiter=",", index_col=None, header=0, dtype=str)
ppd_df = ppd_df.datalabs.rename_in_upper_case()

logging.info('FILTERING DATA - DPC PHYSICIANS WITHOUT PHONE NUMBERS')
ppd_null_df = ppd_df[ppd_df[phone_var_name].isna()]
ppd_dpc_df = ppd_null_df[ppd_null_df['TOP_CD'] == '020']


ppd_ent_key_df = ppd_dpc_df.merge(entity_key_df, how='inner', left_on='ME', right_on='me')
ppd_ent_key_df = ppd_ent_key_df.sort_values('ME').groupby('ME').first().reset_index()

logging.info('FILTERING DATA - NO-CONTACT')
ppd_contact_df = ppd_ent_key_df[~ppd_ent_key_df['entity_id'].isin(no_contact_df['entity_id'])]

logging.info('GETTING LICENSE INFO')
uniq_act_license_df = active_license_df.sort_values('lic_exp_dt', 
                                                    ascending=False).groupby('entity_id').first().reset_index()

ppd_lic_df = ppd_contact_df.merge(uniq_act_license_df, how='inner', on='entity_id')

ppd_lic_df['lic_state'] = ppd_lic_df.loc[:, 'state_cd']

ppd_lic_df['medschool_key'] = ppd_lic_df['MEDSCHOOL_STATE'] + ppd_lic_df['MEDSCHOOL_ID']

ppd_party_key_df = ppd_lic_df.merge(party_key_df, how='inner', left_on='medschool_key',  right_on='KEY_VAL')

ppd_med_name_df = ppd_party_key_df.merge(act_grad_name_df, how='inner', on='PARTY_ID')

ppd_spec_desc_df = ppd_med_name_df.merge(spec_desc_df, how='inner', left_on='PRIM_SPEC_CD',
                                         right_on='spec_cd')
ppd_spec_desc_df = ppd_spec_desc_df.rename(columns={'description': 'spec_description'})
ppd_spec_desc_df['specialty'] = ppd_spec_desc_df['spec_description']

logging.info('ASSIGNING DEGREE TYPE VALUES - MD / DO')
ppd_spec_desc_df['degree_type'] = 'MD'
do_ndx = ppd_spec_desc_df['MD_DO_CODE'] == 2
ppd_spec_desc_df.loc[do_ndx, 'degree_type'] = 'DO'

ppd_uniq_df = ppd_spec_desc_df.groupby(['FIRST_NAME', 'LAST_NAME', 'MEDSCHOOL_GRAD_YEAR', 
                                        'lic_state']).apply(lambda x: x.sample(1)).reset_index(drop=True)

logging.info(f'CREATING SAMPLE - BATCH SIZE - {batch_size}')
batch_df = ppd_uniq_df.sample(batch_size)


filtered_ent_comm_df = entity_comm_me_df[entity_comm_me_df['entity_id'].isin(batch_df['entity_id'])]
uniq_ent_comm_df = filtered_ent_comm_df.sort_values(['entity_id', 
                                                     'aims_phone']).groupby(['entity_id', 'aims_phone']).first().reset_index()
    
uniq_ent_ids = list(uniq_ent_comm_df['entity_id'].unique())

logging.info('ADDING PREVIOUS PHONE NUMBERS TO SAMPLE')
old_phone_df, oldphone_name_list = get_old_phones(uniq_ent_comm_df, uniq_ent_ids)

int_batch_df = batch_df.merge(old_phone_df, how='left', on='entity_id')

int_save_file = out_dir + start_time_str + '_' + str(batch_size) + '_VT_Sample_Internal.xlsx'
writer = pd.ExcelWriter(int_save_file, engine='xlsxwriter')
int_batch_df.to_excel(writer, index=None, header=True)
writer.save()


vt_batch_cols = base_vt_batch_cols + oldphone_name_list

vt_batch_df = int_batch_df[vt_batch_cols]
vt_save_file = out_dir + start_time_str + '_' + str(batch_size) + '_VT_Sample.xlsx'

logging.info(f'SAVING FILE - DESTINATION - {vt_save_file}')
writer = pd.ExcelWriter(vt_save_file, engine='xlsxwriter')
vt_batch_df.to_excel(writer, index=None, header=True)
writer.save()

logging.info('SAMPLE GENERATION COMPLETE.')





























