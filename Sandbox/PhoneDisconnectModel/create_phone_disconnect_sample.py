# Kari Palmier    7/31/19    Created
# Kari Palmier    8/14/19    Updated to work with more generic get_sample
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
gen_path = base_path + 'Common_Model_Code\\'
sys.path.insert(0, gen_path)

from create_model_sample import get_sample, format_phone_sample_cols

gen_path = base_path + 'Common_Code\\'
sys.path.insert(0, gen_path)

from exclude_phone_samples import exclude_phone_samples
from select_files import select_files
from get_ddb_logins import get_ddb_logins
from get_aims_db_tables import get_pe_description, get_aims_connection, get_entity_me_key, get_no_contacts

import warnings
warnings.filterwarnings("ignore")

    
sample_vars = ['ppd_me', 'ppd_first_name', 'ppd_middle_name', 'ppd_last_name', 'ppd_suffix', \
         'ppd_polo_mailing_line_1', 'ppd_polo_mailing_line_2', 'ppd_polo_city', \
         'ppd_polo_state', 'ppd_polo_zip', 'ppd_telephone_number', 'ppd_prim_spec_cd', \
         'pe_description', 'ppd_pe_cd_pad', 'ppd_fax_number', 'pred_class', 'pred_probability']


root = tk.Tk()
root.withdraw()


ddb_info_file = filedialog.askopenfilename(initialdir = "C:\\",
                                         title = "Choose txt file with database login information...")

init_exclude_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Survey_Samples\\'
print('ME and phone numbers from all past month and other current month sample files must be excluded.')
print('The following prompts will select each file to exclude.')
exclude_list = select_files(init_exclude_dir, 'Select sample file(s) to exclude')
    
# Get model file needed
scored_ppd_file = filedialog.askopenfilename(initialdir = "U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Phone_Disconnect_Model\\",
                                         title = "Choose the scored PPD file...")

    
init_save_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\'
out_dir = filedialog.askdirectory(initialdir = init_save_dir,
                                         title = "Choose directory to save sample in...")
out_dir = out_dir.replace("/", "\\")
out_dir += "\\"

support_dir = out_dir + 'Support_Files\\'
if not os.path.exists(support_dir):
    os.mkdir(support_dir)

current_time = datetime.datetime.now()
start_time_str = current_time.strftime("%Y-%m-%d")


# Get ddb login information
ddb_login_dict = get_ddb_logins(ddb_info_file)

if 'AIMS' not in ddb_login_dict.keys():
    print('AIMS login information not present.')
    sys.exit()
   
# Connect to AIMS production database
AIMS_conn = get_aims_connection(ddb_login_dict['AIMS']['username'], ddb_login_dict['AIMS']['password'])

pe_desc_df = get_pe_description(AIMS_conn)

no_contact_df = get_no_contacts(AIMS_conn)

entity_key_df = get_entity_me_key(AIMS_conn)

AIMS_conn.close()

pe_desc_df = pe_desc_df.rename(columns = {'description':'PE_DESCRIPTION'})

no_contact_df = no_contact_df.merge(entity_key_df, how = 'inner', on = 'entity_id')


model_pred_df =  pd.read_csv(scored_ppd_file, delimiter = ",", index_col = None, header = 0, dtype = 'object')

model_pred_df = model_pred_df.rename(columns = {'ppd_me':'ME', 'ppd_telephone_number':'TELEPHONE_NUMBER'})
model_pred_df = model_pred_df.rename(columns = {'PPD_ME':'ME', 'PPD_TELEPHONE_NUMBER':'TELEPHONE_NUMBER'})
model_pred_df = model_pred_df.rename(columns = {'PPD_PE_CD':'PE_CD'})
model_pred_df = model_pred_df.rename(columns = {'ppd_pe_cd':'PE_CD'})

model_pred_df['ME'] =  model_pred_df['ME'].apply(lambda x: '{0:0>11}'.format(x))
model_pred_df['PE_CD'] =  model_pred_df['PE_CD'].apply(lambda x: '{0:0>3}'.format(x))

if 'PE_DESCRIPTION' in list(model_pred_df.columns.values):
    model_pred_df = model_pred_df.drop(['PE_DESCRIPTION'], axis = 1)

ppd_filter_df = exclude_phone_samples(model_pred_df, exclude_list, 'ME', 'TELEPHONE_NUMBER')


ppd_filter_df = ppd_filter_df.merge(pe_desc_df, how = 'inner', 
                                      left_on = 'PE_CD',  right_on ='present_emp_cd')
ppd_filter_df = ppd_filter_df.drop(['present_emp_cd'], axis = 1)

ppd_filter_df = ppd_filter_df[~ppd_filter_df['ME'].isin(no_contact_df['me'])]
    

phone_var_name = 'TELEPHONE_NUMBER'

sample_df, uniq_pred_df = get_sample(model_pred_df, [], [], [], 'pred_probability', phone_var_name, 2, True)     
format_sample_df = format_phone_sample_cols(sample_df, sample_vars)  
  
save_file_pred = support_dir + start_time_str + '_Disconnect_Sample_W_Preds.xlsx'
writer = pd.ExcelWriter(save_file_pred, engine = 'xlsxwriter')
format_sample_df.to_excel(writer, index = None, header = True)
writer.save()
        
format_sample_df = format_sample_df.drop(['PRED_PROBABILITY', 'PRED_CLASS'], axis = 1)

save_file = out_dir + start_time_str + '_Disconnect_Sample.xlsx'
writer = pd.ExcelWriter(save_file, engine = 'xlsxwriter')
format_sample_df.to_excel(writer, index = None, header = True)
writer.save()

no_dup_file = support_dir + start_time_str + 'Phone_Disconnect_Scored_PPD_DPC_Pop_No_Duplicates.csv'
uniq_pred_df = format_phone_sample_cols(uniq_pred_df, sample_vars)  
uniq_pred_df.to_csv(no_dup_file, index = 0, header = 0)

