# Kari Palmier    7/18/19    Created
# Kari Palmier    8/16/19    Added saving printed information to log file
#
#############################################################################

import datetime
import os
import sys
import tkinter as tk
from tkinter import filedialog

import pandas as pd

import settings
from exclude_phone_samples import exclude_phone_samples
from filter_bad_phones import get_good_bad_phones
from get_aims_db_tables import get_no_contacts, get_entity_me_key
from select_files import select_files

from create_model_sample import get_uniq_entries

from   datalabs.access.aims import AIMS
from   datalabs.access.edw import EDW
import datalabs.curate.dataframe  # pylint: disable=unused-import


root = tk.Tk()
root.withdraw()

# Get files needed
ddb_info_file = filedialog.askopenfilename(initialdir="C:\\",
                                           title="Choose txt file with database login information...")

# Get model file needed
ppd_file = filedialog.askopenfilename(initialdir="U:\\Source Files\\Data Analytics\\Data-Science\\Data\\PPD\\",
                                      title="Choose the latest PPD file...")

dhc_file = filedialog.askopenfilename(initialdir="U:\\Source Files\\Data Analytics\\Data-Science\\Data\\DHC\\",
                                      title="Choose combined DHC csv file...")

init_anlys_dir = 'U:\\Source Files\\Data Analytics\\'
anlys_out_dir = filedialog.askdirectory(initialdir=init_anlys_dir,
                                        title="Choose directory to save analysis output...")
anlys_out_dir = anlys_out_dir.replace("/", "\\")
anlys_out_dir += "\\"

init_save_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Survey_Samples\\DHC\\'
sample_out_dir = filedialog.askdirectory(initialdir=init_save_dir,
                                         title="Choose directory to save sample in...")
sample_out_dir = sample_out_dir.replace("/", "\\")
sample_out_dir += "\\"

init_exclude_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Survey_Samples\\'
print('ME and phone numbers from all past month and other current month sample files must be excluded.')
print('The following prompts will select each file to exclude.')
exclude_list = select_files(init_exclude_dir, 'Select sample file(s) to exclude')

sample_str = input('Enter the sample size (all = all samples in bin): ')
if sample_str.lower() == 'all' or not(sample_str.isnumeric()):
    sample_size = 'all'
else:
    sample_size = int(sample_str)

# Get current date for output file names
current_time = datetime.datetime.now()
start_time_str = current_time.strftime("%Y-%m-%d")

# Create log file
old_stdout = sys.stdout
log_filename = anlys_out_dir + start_time_str + '_DHC_Sample_Analysis_Log' + '.txt'
log_file = open(log_filename, "w")
sys.stdout = log_file


with EDW() as edw:
  npi_me_df = edw.get_me_npi_mapping()


with AIMS() as aims:
  entity_key_df = get_entity_me_key(aims._connection)
  no_contact_df = get_no_contacts(aims._connection)
   
# Load PPD csv file
ppd_df = pd.read_csv(ppd_file, delimiter=",", index_col=None, header=0, dtype=str)
ppd_df = ppd_df.datalabs.rename_in_upper_case()

ppd_ent_key_df = ppd_df.merge(entity_key_df, how='inner', left_on='ME', right_on='me')

ppd_contact_df = ppd_ent_key_df[~ppd_ent_key_df['entity_id'].isin(no_contact_df['entity_id'])]


# Load DHC csv file
dhc_df = pd.read_csv(dhc_file, delimiter=",", index_col=None, header=0, dtype=str)

# Convert query return ME and NPI colums to be compatible with other tables
#npi_me_df['ME'] = npi_me_df['ME'].astype('str')
#npi_me_df['NPI_NBR'] = npi_me_df['NPI_NBR'].astype('str')


print('-------------------------------------------')
print('DHC and Masterfile Data Comparison Analysis')
print('-------------------------------------------')
print('\n')

# Join the query results and the PPD data (will add NPI and party ID to PPD data)
ppd_npi_df = npi_me_df.merge(ppd_contact_df, how='inner', on='ME')

# Extract only DHC entries that are not registered in the Do Not Call Registry
dhc_ok_df = dhc_df[dhc_df['Do Not Call Registry'] != 'Registered']
dhc_ok_df = dhc_ok_df.datalabs.rename_in_upper_case()


print('Total number of DHC entries: {}'.format(dhc_df.shape[0]))
print('Total number of DHC not in Do Not Call registery: {}'.format(dhc_ok_df.shape[0]))
print('\n')


###### Get entries in DHC that are not in PPD

dhc_ppd_null_df = dhc_ok_df.merge(ppd_npi_df, how = 'left', right_on= 'NPI_NBR' , left_on = 'NPI')
dhc_only_df = dhc_ppd_null_df[dhc_ppd_null_df['NPI_NBR'].isna()]

print('Number DHC entries missing from PPD: {}'.format(dhc_only_df.shape[0]))


###### Get entries in PPD that are not in DHC

ppd_dhc_null_df = dhc_ok_df.merge(ppd_npi_df, how='right', right_on='NPI_NBR', left_on='NPI')
ppd_only_df = ppd_dhc_null_df[ppd_dhc_null_df['NPI'].isna()]

print('Number PPD entries missing from DHC: {}'.format(ppd_only_df.shape[0]))
print('\n')

###### Get entries with matching NPI in PPD and DHC

#npi_match_df = pd.merge(right = ppd_npi_df, left = dhc_ok_df, right_on= 'NPI_NBR_NUM' , left_on = 'NPI', how = 'inner')

npi_match_df = dhc_ok_df.merge(ppd_npi_df, how='inner', left_on='NPI', right_on='NPI_NBR')
print('Number PPD and DHC entries with matching NPI numbers: {}'.format(npi_match_df.shape[0]))
print('\n')

# Find entries that do not have a PPD or DHC phone number
no_ppd_phone_ndx = npi_match_df['TELEPHONE_NUMBER'].isna()
no_dhc_phone_ndx = npi_match_df['PHONE NUMBER'].isna()


# Find entries that do not have a PPD phone number
match_no_ppd_phone_df = npi_match_df.loc[no_ppd_phone_ndx, :]

print('Number matching entries missing PPD phone number: {}'.format(match_no_ppd_phone_df.shape[0]))

# Find entries that do not have a DHC phone number
match_no_dhc_phone_df = npi_match_df.loc[no_dhc_phone_ndx, :]

print('Number matching entries missing DHC phone number: {}'.format(match_no_dhc_phone_df.shape[0]))
print('\n')

# Find entries that have PPD and DHC phone numbers
match_no_nan_df = npi_match_df.loc[~no_ppd_phone_ndx & ~no_dhc_phone_ndx, :]

print('Number of matching entries with DHC and PPD phone numbers: {}'.format(match_no_nan_df.shape[0]))

# Convert DHC and PPD phone numbers to the same format 
match_no_nan_df['PHONE NUMBER'] = match_no_nan_df['PHONE NUMBER'].apply(lambda x: x.replace('.', ''))
#match_no_nan_df['TELEPHONE_NUMBER'] = match_no_nan_df['TELEPHONE_NUMBER'].astype('str')
#match_no_nan_df['PPD_Phone_Number'] = match_no_nan_df['PPD_Phone_Number'].apply(lambda x: x.replace('.0', ''))

# Find entries with matching PPD and DHC phone numbers
same_ndx = match_no_nan_df['PHONE NUMBER'] == match_no_nan_df['TELEPHONE_NUMBER']
same_phone_df = match_no_nan_df.loc[same_ndx, :]

print('Number of matching entries with same phone numbers: {}'.format(same_phone_df.shape[0]))

diff_ndx = ~same_ndx
diff_phone_df = match_no_nan_df.loc[diff_ndx, :]

print('Number of matching entries with different phone numbers: {}'.format(diff_phone_df.shape[0]))
print('\n')

print('----------------------------')
print('DHC DPC Sampling Information')
print('----------------------------')
print('\n')

orig_rename_dict = {'POLO_MAILING_LINE_2':'ORIG_PPD_POLO_MAILING_LINE_2', 'POLO_MAILING_LINE_1':'ORIG_PPD_POLO_MAILING_LINE_1',
                   'POLO_CITY':'ORIG_PPD_POLO_CITY', 'POLO_STATE':'ORIG_PPD_POLO_STATE', 'POLO_ZIP':'ORIG_PPD_POLO_ZIP',
                   'TELEPHONE_NUMBER':'ORIG_PPD_TELEPHONE_NUMBER'}

new_rename_dict = {'ADDRESS':'POLO_MAILING_LINE_2', 'ADDRESS1':'POLO_MAILING_LINE_1',
                   'CITY_x':'POLO_CITY', 'STATE_x':'POLO_STATE', 'ZIP CODE':'POLO_ZIP', 'PHONE NUMBER':'TELEPHONE_NUMBER'}


# Find entries that do have a DHC phone number
npi_match_dpc_df = npi_match_df[npi_match_df['TOP_CD'] == '020']
print('Number of direct patient care (DPC) matching entries: {}'.format(npi_match_dpc_df.shape[0]))
print('\n')


match_dhc_phone_df = npi_match_dpc_df.loc[~no_dhc_phone_ndx, :]
print('Number of direct patient care (DPC) matching entries with DHC phone numbers: {}'.format(match_dhc_phone_df.shape[0]))
print('\n')

match_dhc_phone_df['PHONE NUMBER'] = match_dhc_phone_df['PHONE NUMBER'].apply(lambda x: x.replace('.', ''))

match_dhc_phone_df = match_dhc_phone_df.rename(columns=orig_rename_dict)

match_dhc_phone_df = match_dhc_phone_df.rename(columns=new_rename_dict)
    
match_dhc_phone_df = match_dhc_phone_df.drop(['me'], axis=1)


phone_var_name = 'TELEPHONE_NUMBER'

print('DHC Sample Size = {}'.format(sample_size))

ppd_dhc_filter_df = exclude_phone_samples(match_dhc_phone_df, exclude_list, 'ME', phone_var_name)

bad_df, ppd_dhc_filter_df = get_good_bad_phones(ppd_dhc_filter_df, phone_var_name)

ppd_dhc_uniq_df = get_uniq_entries(ppd_dhc_filter_df, 'ME', phone_var_name, '', 1, True)

if sample_size == 'all':
    sample_df = ppd_dhc_uniq_df
else:
    sample_df = ppd_dhc_uniq_df.sample(sample_size)

out_sample_vars = ['NPI', 'ME', 'FIRST_NAME', 'MIDDLE_NAME', 'LAST_NAME', 'SUFFIX', 'POLO_MAILING_LINE_2', 
                   'POLO_MAILING_LINE_1', 'POLO_CITY', 'POLO_STATE', 'POLO_ZIP', 'TELEPHONE_NUMBER']

sample_out_df = sample_df[out_sample_vars]

save_file = sample_out_dir + start_time_str + '_DHC_Sample.xlsx'
writer = pd.ExcelWriter(save_file, engine='xlsxwriter')
sample_out_df.to_excel(writer, index=None, header=True)
writer.save()

int_sample_vars = ['NPI', 'ME', 'FIRST_NAME', 'MIDDLE_NAME', 'LAST_NAME', 'SUFFIX', 'POLO_MAILING_LINE_2', 
                   'POLO_MAILING_LINE_1', 'POLO_CITY', 'POLO_STATE', 'POLO_ZIP', 'TELEPHONE_NUMBER',  
                   'ORIG_PPD_POLO_MAILING_LINE_2', 'ORIG_PPD_POLO_MAILING_LINE_1', 'ORIG_PPD_POLO_CITY', 
                   'ORIG_PPD_POLO_STATE', 'ORIG_PPD_POLO_ZIP', 'ORIG_PPD_TELEPHONE_NUMBER']

sample_int_df = sample_df[int_sample_vars]

int_save_file = sample_out_dir + start_time_str + '_DHC_Sample_Internal.xlsx'
writer = pd.ExcelWriter(int_save_file, engine='xlsxwriter')
sample_int_df.to_excel(writer, index=None, header=True)
writer.save()

# change logging back to console and close log file
sys.stdout = old_stdout
log_file.close()











