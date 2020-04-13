# Kari Palmier    8/22/19    Created
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
from filter_bad_phones import get_good_bad_phones
from select_files import select_files
from get_ods_db_tables import get_symphony_sample_info
from get_aims_db_tables import get_no_contacts, get_pe_description, get_entity_me_key
from rename_competitor_sample import rename_competitor_sample
import datalabs.curate.dataframe as df
from create_model_sample import get_uniq_entries
from datalabs.access.aims import AIMS
from datalabs.access.ods import ODS

warnings.filterwarnings("ignore")


sample_col_names = ['ME', 'FIRST_NAME', 'MIDDLE_NAME', 'LAST_NAME', 'SUFFIX',
         'POLO_MAILING_LINE_1', 'POLO_MAILING_LINE_2', 'POLO_CITY',
         'POLO_STATE', 'POLO_ZIP', 'TELEPHONE_NUMBER', 'PRIM_SPEC_CD',
         'DESCRIPTION', 'PE_CD', 'FAX_NUMBER']

root = tk.Tk()
root.withdraw()

data_sel = input('Select existing Symphony data csv file? (y/[n]): ')
if data_sel.lower().find('y') < 0:
    data_sel = 'n'
else:
    sym_file = filedialog.askopenfilename(initialdir="U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Symphony\\",
                                          title="Choose the Symphony data csv file...")

# Get files needed
ddb_info_file = filedialog.askopenfilename(initialdir="C:\\",
                                           title="Choose txt file with database login information...")

# Get model file needed
ppd_file = filedialog.askopenfilename(initialdir="U:\\Source Files\\Data Analytics\\Data-Science\\Data\\PPD\\",
                                      title="Choose the latest PPD file...")

init_save_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Survey_Samples\\Symphony\\'
out_dir = filedialog.askdirectory(initialdir=init_save_dir,
                                  title="Choose directory to save sample in...")
out_dir = out_dir.replace("/", "\\")
out_dir += "\\"

support_dir = out_dir + 'Support_Files\\'
if not os.path.exists(support_dir):
    os.mkdir(support_dir)

init_exclude_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Survey_Samples\\'
print('ME and phone numbers from all past month and other current month sample files must be excluded.')
print('The following prompts will select each file to exclude.')
exclude_list = select_files(init_exclude_dir, 'Select sample file(s) to exclude')

sample_str = input('Enter the sample size (all = all samples in bin): ')
if sample_str.lower() == 'all' or not(sample_str.isnumeric()):
    sample_size = 'all'
else:
    sample_size = int(sample_str)

current_time = datetime.datetime.now()
start_time_str = current_time.strftime("%Y-%m-%d")

phone_var_name = 'TELEPHONE_NUMBER'

if data_sel == 'n':
    with ODS() as ods:    
        symphony_df = get_symphony_sample_info(ods._connection)
else:
    symphony_df =  pd.read_csv(sym_file, delimiter=",", index_col=None, header=0, dtype=str)

with AIMS() as aims:
    entity_key_df = get_entity_me_key(aims._connection)
    no_contact_df = get_no_contacts(aims._connection)
    pe_desc_df = get_pe_description(aims._connection)
   
ppd_df = pd.read_csv(ppd_file, delimiter=",", index_col=None, header=0, dtype=str)
ppd_df = df.rename_in_upper_case(ppd_df)

ppd_dpc_df = ppd_df[ppd_df['TOP_CD'] == '020']


ppd_ent_key_df = ppd_df.merge(entity_key_df, how='inner', left_on='ME', right_on='me')

ppd_contact_df = ppd_ent_key_df[~ppd_ent_key_df['entity_id'].isin(no_contact_df['entity_id'])]

ppd_pe_df = ppd_contact_df.merge(pe_desc_df, how='inner',
                                 left_on='PE_CD',  right_on='present_emp_cd')


ppd_pe_df['ME_SUBSTR'] = ppd_pe_df['ME'].apply(lambda x: x[:(len(x) - 1)])

ppd_sym_df = ppd_pe_df.merge(symphony_df, how='inner', left_on=['ME_SUBSTR'],  right_on=['SYM_ME'])
ppd_sym_df = df.rename_in_upper_case(ppd_sym_df)

ppd_sym_rename_df = rename_competitor_sample(ppd_sym_df, 'SYM_')
ppd_sym_rename_df = ppd_sym_rename_df[sample_col_names]

ppd_filter_df = exclude_phone_samples(ppd_sym_rename_df, exclude_list, 'ME', phone_var_name)

bad_df, ppd_filter_df = get_good_bad_phones(ppd_filter_df, phone_var_name)

ppd_uniq_df = get_uniq_entries(ppd_filter_df, 'ME', phone_var_name, '', 1, True)

if sample_size == 'all':
    sample_df = ppd_uniq_df
else:
    sample_df = ppd_uniq_df.sample(sample_size)

sample_df = sample_df[sample_col_names]

save_file = out_dir + start_time_str + '_Symphony_Sample.xlsx'
writer = pd.ExcelWriter(save_file, engine='xlsxwriter')
sample_df.to_excel(writer, index=None, header=True)
writer.save()
