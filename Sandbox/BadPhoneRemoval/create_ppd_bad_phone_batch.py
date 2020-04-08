# Kari Palmier    Created 8/12/19
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
from filter_bad_phones import get_good_bad_phones
from create_batch_loads import create_phone_delete
from get_aims_db_tables import get_ent_comm_phones, get_uniq_active_ent_info

warnings.filterwarnings("ignore")


root = tk.Tk()
root.withdraw()

init_ppd_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\PPD\\'
ppd_file = filedialog.askopenfilename(initialdir = init_ppd_dir,
                                         title = "Choose latest PPD CSV file...")

# Get files needed
ddb_info_file = filedialog.askopenfilename(initialdir = "C:\\",
                                         title = "Choose txt file with database login information...")

init_anlys_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\PPD\\Analysis\\'
anlys_out_dir = filedialog.askdirectory(initialdir = init_anlys_dir,
                                         title = "Choose directory to save analysis output...")
anlys_out_dir = anlys_out_dir.replace("/", "\\")
anlys_out_dir += "\\"

support_dir = anlys_out_dir + 'Support\\'
if not os.path.exists(support_dir):
    os.mkdir(support_dir)

init_batch_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\IT_BatchLoads\\Humach_Surveys\\'
batch_out_dir = filedialog.askdirectory(initialdir = init_batch_dir,
                                         title = "Choose directory to save removal batch file output...")
batch_out_dir = batch_out_dir.replace("/", "\\")
batch_out_dir += "\\"

# Get current date for output file names
current_time = datetime.datetime.now()
start_time_str = current_time.strftime("%Y-%m-%d")

# Name output files
anlys_out_file =  anlys_out_dir + start_time_str + '_Bad_Source_Counts.xlsx'
bad_data_file = support_dir + start_time_str + '_PPD_Bad_Entries.csv'
good_data_file = support_dir + start_time_str + '_PPD_Good_Entries.csv'
batch_out_file = batch_out_dir + 'HSG_PHYS_DELETES_' + start_time_str + '_PPD_Bad.csv'

dot_ndx = ppd_file.find('.')
ppd_file = ppd_file.replace('/', '\\')
slash_ndx = [i for i in range(len(ppd_file)) if ppd_file.startswith('\\', i)]
clean_ppd_file = support_dir + ppd_file[slash_ndx[-1] + 1:dot_ndx] + '_Cleaned_Phones' + ppd_file[dot_ndx:]

# Create log file
old_stdout = sys.stdout
log_filename = anlys_out_dir + start_time_str + '_PPD_Bad_Phone_Batch_Log.txt'
log_file = open(log_filename, "w")
sys.stdout = log_file

  
# Read PPD and find only non-null TELEPHONE NUMBER entries
ppd_df = pd.read_csv(ppd_file, delimiter = ",", index_col = None, header = 0, dtype = str)
ppd_not_null_df = ppd_df[ppd_df['TELEPHONE_NUMBER'].notnull()]

# get entity_comm_at, phone_at, and me info for latest begin date of each me/entity_id
with AIMS() as aims:
    entity_comm_me_df = get_ent_comm_phones(aims._connection)

entity_uniq_no_end_df = get_uniq_active_ent_info(entity_comm_me_df, 'aims_phone', 'begin_dt', 'end_dt')

# Add entity_comm_at info to PPD
ppd_entity_df = ppd_not_null_df.merge(entity_uniq_no_end_df, how = 'inner', 
                                      left_on = ['ME', 'TELEPHONE_NUMBER'],
                                      right_on = ['me', 'aims_phone'])

print('-----------------------------------------------------------------------------------------')
print('Entire PPD Results')
print('-----------------------------------------------------------------------------------------')
print('Total number of PPD original entries: {}'.format(ppd_df.shape[0]))    
print('Number of PPD entries with phone numbers: {}'.format(ppd_not_null_df.shape[0]))
print('Number of PPD entries with entity information: {}'.format(ppd_entity_df.shape[0]))
print('\n')

print('Entire PPD Bad Entry Removal Results')
print('------------------------------------')

# Get list of good and bad phone numbers
bad_df, good_df = get_good_bad_phones(ppd_entity_df, 'TELEPHONE_NUMBER')

# create counts of different source types of whole PPD to save
bad_src_cnt = bad_df.sort_values(['src_cat_code']).groupby(['src_cat_code']).size().reset_index()
bad_src_cnt = bad_src_cnt.rename(columns = {0:'count'})

# Get DPC only good and bad entries
bad_dpc_df = bad_df[bad_df['TOP_CD'] == '020']

good_dpc_df = good_df[good_df['TOP_CD'] == '020']
ppd_dpc_df = ppd_df[ppd_df['TOP_CD'] == '020']

print('\n')
print('-----------------------------------------------------------------------------------------')
print('DPC Only Results')
print('-----------------------------------------------------------------------------------------')
print('Total number of DPC original entries: {}'.format(ppd_dpc_df.shape[0]))    
print('Number of DPC original entries with phone numbers: {}'.format(sum(ppd_dpc_df['TELEPHONE_NUMBER'].notnull())))
print('Number of DPC bad phone entries: {}'.format(bad_dpc_df.shape[0]))    
print('Number of DPC good phone entries: {}'.format(good_dpc_df.shape[0]))    

# create counts of different source types of DPC PPD entries to save
bad_dpc_src_cnt = bad_dpc_df.sort_values(['src_cat_code']).groupby(['src_cat_code']).size().reset_index()
bad_dpc_src_cnt = bad_dpc_src_cnt.rename(columns = {0:'count'})

# Create a batch of bad numbers to be deleted from the PPD (all, not DPC only)
bad_batch = create_phone_delete(bad_df, 'ME', 'TELEPHONE_NUMBER')
bad_batch.to_csv(batch_out_file, index = False, header = True)

# Save source count information
writer = pd.ExcelWriter(anlys_out_file, engine = 'xlsxwriter')
bad_src_cnt.to_excel(writer, sheet_name = 'all_bad_source_counts', index = False, header = 0)
bad_dpc_src_cnt.to_excel(writer, sheet_name = 'dpc_bad_source_counts', index = False, header = 0)
writer.save()

bad_df.to_csv(bad_data_file, index = False, header = True)       
good_df.to_csv(good_data_file, index = False, header = True)       


ppd_cols = list(ppd_df.columns.values)

clean_ppd_df = good_df[ppd_cols]
clean_ppd_df.to_csv(clean_ppd_file, index = False, header = True)       


sys.stdout = old_stdout
log_file.close()







