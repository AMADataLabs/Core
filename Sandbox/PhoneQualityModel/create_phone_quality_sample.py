# Kari Palmier    7/31/19    Created
# Kari Palmier    8/14/19    Updated to work with more generic get_sample
#
#############################################################################
import datetime
import os
import sys
import tkinter as tk
from tkinter import filedialog
import warnings

import pandas as pd

import settings
from exclude_phone_samples import exclude_phone_samples
from select_files import select_files
from get_aims_db_tables import get_pe_description, get_entity_me_key, get_no_contacts

from create_model_sample import get_phone_sample, format_phone_sample_cols
from datalabs.access.aims import AIMS

warnings.filterwarnings("ignore")





sample_vars = ['ppd_me', 'ppd_first_name', 'ppd_middle_name', 'ppd_last_name', 'ppd_suffix',
               'ppd_polo_mailing_line_1', 'ppd_polo_mailing_line_2', 'ppd_polo_city',
               'ppd_polo_state', 'ppd_polo_zip', 'ppd_telephone_number', 'ppd_prim_spec_cd',
               'pe_description', 'ppd_pe_cd', 'ppd_fax_number', 'pred_class', 'pred_probability']

root = tk.Tk()
root.withdraw()


ddb_info_file = filedialog.askopenfilename(initialdir="C:\\",
                                           title="Choose txt file with database login information...")

# Get model file needed
scored_ppd_file = filedialog.askopenfilename(initialdir="U:\\Source Files\\Data Analytics\\Data-Science\\" +
                                                        "Data\\Phone_Quality_Model\\",
                                             title="Choose the scored PPD file...")

init_exclude_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Survey_Samples\\'
print('ME and phone numbers from all past month and other current month sample files must be excluded.')
print('The following prompts will select each file to exclude.')
exclude_list = select_files(init_exclude_dir, 'Select sample file(s) to exclude')
    
init_save_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Survey_Samples\\Standard\\'
out_dir = filedialog.askdirectory(initialdir=init_save_dir,
                                  title="Choose directory to save sample in...")
out_dir = out_dir.replace("/", "\\")
out_dir += "\\"

support_dir = out_dir + 'Support_Files\\'
if not os.path.exists(support_dir):
    os.mkdir(support_dir)

current_time = datetime.datetime.now()
start_time_str = current_time.strftime("%Y-%m-%d")


print('Pulling data.')
with AIMS() as aims:
  pe_desc_df = get_pe_description(aims._connection)
  print('pe_description complete')
  no_contact_df = get_no_contacts(aims._connection)
  print('no_contacts complete')
  entity_key_df = get_entity_me_key(aims._connection)
  print('entity_me_key complete')

pe_desc_df = pe_desc_df.rename(columns={'description': 'PE_DESCRIPTION'})

no_contact_df = no_contact_df.merge(entity_key_df, how='inner', on='entity_id')

print('Reading scored PPD.')
model_pred_df = pd.read_csv(scored_ppd_file, delimiter=",", index_col=None, header=0, dtype=str)

model_pred_df = model_pred_df.rename(columns={'ppd_me': 'ME', 'ppd_telephone_number': 'TELEPHONE_NUMBER'})
model_pred_df = model_pred_df.rename(columns={'PPD_ME': 'ME', 'PPD_TELEPHONE_NUMBER': 'TELEPHONE_NUMBER'})
model_pred_df = model_pred_df.rename(columns={'PPD_PE_CD': 'PE_CD'})
model_pred_df = model_pred_df.rename(columns={'ppd_pe_cd': 'PE_CD'})

model_pred_df['ME'] = model_pred_df['ME'].apply(lambda x: '{0:0>11}'.format(x))
model_pred_df['PE_CD'] = model_pred_df['PE_CD'].apply(lambda x: '{0:0>3}'.format(x))

if 'PE_DESCRIPTION' in list(model_pred_df.columns.values):
    model_pred_df = model_pred_df.drop(['PE_DESCRIPTION'], axis=1)

print('Making exclusions.')
ppd_filter_df = exclude_phone_samples(model_pred_df, exclude_list, 'ME', 'TELEPHONE_NUMBER')


ppd_filter_df = ppd_filter_df.merge(pe_desc_df, how='inner',
                                    left_on='PE_CD',  right_on='present_emp_cd')
ppd_filter_df = ppd_filter_df.drop(['present_emp_cd'], axis=1)

ppd_uniq_df = ppd_filter_df[~ppd_filter_df['ME'].isin(no_contact_df['me'])]
    
print('Making sample.')
phone_var_name = 'TELEPHONE_NUMBER'
num_duplicate_phones = 10

print('Running quality checks on phone field.')
import numpy as np
# remove records with nulls, nans, empty strings in phone col
ppd_uniq_df = ppd_uniq_df[ppd_uniq_df[phone_var_name].apply(lambda x: x not in ['', 'nan', np.nan])]
ppd_uniq_df = ppd_uniq_df[ppd_uniq_df[phone_var_name].notnull()]
ppd_uniq_df = ppd_uniq_df[ppd_uniq_df[phone_var_name].notna()]

# check to make sure each phone entry is a 10-digit number
phone_numbers = ppd_uniq_df[phone_var_name].values
assert([n.isdigit() for n in phone_numbers])

sample_df, filtered_df = get_phone_sample(ppd_filter_df, [], [], [],
                                          'PRED_PROBABILITY', phone_var_name, 1, 'ME',
                                          num_duplicate_phones, True)

pred_cols = ['PRED_CLASS', 'PRED_PROBABILITY']
for c in pred_cols:
    if c not in sample_df.columns.values:
        sample_df[c] = 1.0

format_sample_df, new_col_names = format_phone_sample_cols(sample_df, sample_vars)  
  
save_file_pred = support_dir + start_time_str + '_Masterfile_Model_Sample_W_Preds.xlsx'
writer = pd.ExcelWriter(save_file_pred, engine='xlsxwriter')
format_sample_df.to_excel(writer, index=None, header=True)
writer.save()

for c in pred_cols:
    if c not in format_sample_df.columns.values:
        pred_cols.remove(c)

format_sample_df.drop(pred_cols, axis=1, inplace=True)

save_file = out_dir + start_time_str + '_Masterfile_Model_Sample.xlsx'
writer = pd.ExcelWriter(save_file, engine='xlsxwriter')
format_sample_df.to_excel(writer, index=None, header=True)
writer.save()

no_dup_file = support_dir + start_time_str + '_Phone_Quality_Scored_PPD_DPC_Pop_For_Sample.csv'
filtered_df, temp_cols = format_phone_sample_cols(filtered_df, sample_vars)  
filtered_df.to_csv(no_dup_file, index=0, header=0)

print('Complete.')
