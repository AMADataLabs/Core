# Kari Palmier    8/30/19    Created
#
#############################################################################
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import datetime

# Get path of general (common) code and add it to the python path variable
import sys
import os
curr_path = os.path.abspath(__file__)
slash_ndx = [i for i in range(len(curr_path)) if curr_path.startswith('\\', i)]
base_path = curr_path[:slash_ndx[-2]+1]
gen_path = base_path + 'CommonCode\\'
sys.path.insert(0, gen_path)

from get_ddb_logins import get_ddb_logins
from get_aims_db_tables import get_no_contacts, get_active_licenses, get_ent_comm_phones
from get_aims_db_tables import get_spec_description, get_entity_me_key, get_aims_connection
from get_edw_db_tables import get_party_keys, get_active_gradschool_name, get_edw_connection
from capitalize_column_names import capitalize_column_names

gen_path = base_path + 'CommonModelCode\\'
sys.path.insert(0, gen_path)

import warnings
warnings.filterwarnings("ignore")


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

# Get ddb login information
ddb_login_dict = get_ddb_logins(ddb_info_file)

if 'EDW' not in ddb_login_dict.keys():
    print('EDW login information not present.')
    sys.exit()

if 'AIMS' not in ddb_login_dict.keys():
    print('AIMS login information not present.')
    sys.exit()

EDW_conn = get_edw_connection(ddb_login_dict['EDW']['username'], ddb_login_dict['EDW']['password'])

print('Starting...')


print('Pulling EDW data.')
party_key_df = get_party_keys(EDW_conn, 23)
act_grad_name_df = get_active_gradschool_name(EDW_conn)

EDW_conn.close()

print('Pulling AIMS data.')
AIMS_conn = get_aims_connection(ddb_login_dict['AIMS']['username'], ddb_login_dict['AIMS']['password'])

entity_key_df = get_entity_me_key(AIMS_conn)
entity_comm_me_df = get_ent_comm_phones(AIMS_conn)
no_contact_df = get_no_contacts(AIMS_conn)
active_license_df = get_active_licenses(AIMS_conn)
spec_desc_df = get_spec_description(AIMS_conn)

AIMS_conn.close()
print('Pulling PPD.')
ppd_df = pd.read_csv(ppd_file, delimiter=",", index_col=None, header=0, dtype=str)
ppd_df = capitalize_column_names(ppd_df)

print('Starting a bunch of shit')
ppd_null_df = ppd_df[ppd_df[phone_var_name].isna()]
ppd_dpc_df = ppd_null_df[ppd_null_df['TOP_CD'] == '020']


ppd_ent_key_df = ppd_dpc_df.merge(entity_key_df, how='inner', left_on='ME', right_on='me')
ppd_ent_key_df = ppd_ent_key_df.sort_values('ME').groupby('ME').first().reset_index()


ppd_contact_df = ppd_ent_key_df[~ppd_ent_key_df['entity_id'].isin(no_contact_df['entity_id'])]
print('Doing more shit')
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
print('More shit')
ppd_spec_desc_df['degree_type'] = 'MD'
do_ndx = ppd_spec_desc_df['MD_DO_CODE'] == 2
ppd_spec_desc_df.loc[do_ndx, 'degree_type'] = 'DO'

ppd_uniq_df = ppd_spec_desc_df.groupby(['FIRST_NAME', 'LAST_NAME', 'MEDSCHOOL_GRAD_YEAR', 
                                        'lic_state']).apply(lambda x: x.sample(1)).reset_index(drop=True)

batch_df = ppd_uniq_df.sample(batch_size)


filtered_ent_comm_df = entity_comm_me_df[entity_comm_me_df['entity_id'].isin(batch_df['entity_id'])]
uniq_ent_comm_df = filtered_ent_comm_df.sort_values(['entity_id', 
                                                     'aims_phone']).groupby(['entity_id', 'aims_phone']).first().reset_index()
    
uniq_ent_ids = list(uniq_ent_comm_df['entity_id'].unique())
print('Even more shit, somehow')
old_phone_df, oldphone_name_list = get_old_phones(uniq_ent_comm_df, uniq_ent_ids)

int_batch_df = batch_df.merge(old_phone_df, how='left', on='entity_id')

int_save_file = out_dir + start_time_str + '_' + str(batch_size) + '_VT_Sample_Internal.xlsx'
writer = pd.ExcelWriter(int_save_file, engine='xlsxwriter')
int_batch_df.to_excel(writer, index=None, header=True)
writer.save()


vt_batch_cols = base_vt_batch_cols + oldphone_name_list

vt_batch_df = int_batch_df[vt_batch_cols]
vt_save_file = out_dir + start_time_str + '_' + str(batch_size) + '_VT_Sample.xlsx'
print('FINALLY. Saving to csv at {}'.format(vt_save_file))
writer = pd.ExcelWriter(vt_save_file, engine='xlsxwriter')
vt_batch_df.to_excel(writer, index=None, header=True)
writer.save()

print('DONE')





























