# Kari Palmier    Created 8/26/19
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
gen_path = base_path + 'Common_Code\\'
sys.path.insert(0, gen_path)

from create_batch_loads import create_phone_delete, create_phone_replace
from get_input_date_range import get_input_date_range

import warnings
warnings.filterwarnings("ignore")

    
phone_source = 'PHNSURV'

root = tk.Tk()
root.withdraw()

init_val_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Validation\\'
init_ppd_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\PPD\\'
init_anlys_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Validation\\Analysis\\'
init_batch_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\IT_BatchLoads\\Humach_Surveys\\'

val_results_file = filedialog.askopenfilename(initialdir=init_val_dir,
                                              title="Choose validation file with results encoded...")

ppd_file = filedialog.askopenfilename(initialdir=init_ppd_dir,
                                      title="Choose latest PPD CSV file...")

anlys_out_dir = filedialog.askdirectory(initialdir=init_anlys_dir,
                                        title="Choose directory to save analysis output...")
anlys_out_dir = anlys_out_dir.replace("/", "\\")
anlys_out_dir += "\\"

support_dir = anlys_out_dir + 'Support\\'
if not os.path.exists(support_dir):
    os.mkdir(support_dir)


batch_out_dir = filedialog.askdirectory(initialdir=init_batch_dir,
                                        title="Choose directory to save update and removal batch file outputs...")
batch_out_dir = batch_out_dir.replace("/", "\\")
batch_out_dir += "\\"

current_time = datetime.datetime.now()
start_time_str = current_time.strftime("%Y-%m-%d")

time_str = input('Do you want to choose a time subset (n will use all data)? (y/[n]): ')

if time_str.lower().find('y') < 0:
    date_range_str = ''
else:
    start_date, end_date, date_range_str = get_input_date_range()


kb_del_all_out_file = support_dir + start_time_str + '_Val_Phones_KnownBad.csv'
kb_del_out_file = batch_out_dir + 'HSG_PHYS_DELETES_' + start_time_str + '_ValKnownBad.csv'
up_all_out_file = support_dir + start_time_str + '_Val_Phones_NewNumbers.csv'
up_add_out_file = batch_out_dir + 'HSG_PHYS_' + phone_source + '_PHONE_' + start_time_str + '_ValUpdates.csv'

# Read in wslive data
val_results_df = pd.read_csv(val_results_file, delimiter=",", index_col=None, header=0, dtype=str)

# Get data for date range specified
val_results_df['LASTCALL'] = pd.to_datetime(val_results_df['LASTCALL'])

if date_range_str != '':
    val_date_df = val_results_df[(val_results_df['LASTCALL'] >= start_date) & \
                                  (val_results_df['LASTCALL'] <= end_date)]
else:
    val_date_df = val_results_df[:]
            
min_date = val_date_df['LASTCALL'].min()
min_time_str = min_date.strftime("%Y-%m-%d")

max_date = val_date_df['LASTCALL'].max()
max_time_str = max_date.strftime("%Y-%m-%d")
         
date_range_str = min_time_str + '_to_' + max_time_str 

log_filename = anlys_out_dir + date_range_str + '_Val_Analysis_Log.txt'
anlys_out_file = anlys_out_dir + date_range_str + '_Val_Result_Counts.xlsx'

old_stdout = sys.stdout
log_file = open(log_filename, "w")
sys.stdout = log_file


# Read in PPD data
ppd_df = pd.read_csv(ppd_file, delimiter = ",", index_col = None, header = 0, dtype = 'object')

all_phone_count = val_date_df.sort_values(['PHONE_STATUS1']).groupby(['PHONE_STATUS1']).size().reset_index()
all_phone_count = all_phone_count.rename(columns = {0:'count'})

all_addr_count = val_date_df.sort_values(['ADDRESS_STATUS1']).groupby(['ADDRESS_STATUS1']).size().reset_index()
all_addr_count = all_addr_count.rename(columns = {0:'count'})

known_bad_df = val_date_df[val_results_df['PHONE_STATUS1'] == 'Known Bad']

all_known_bad_count = known_bad_df.sort_values(['RESULT_OF_CALL']).groupby(['RESULT_OF_CALL']).size().reset_index()
all_known_bad_count = all_known_bad_count.rename(columns = {0:'count'})


month_phone_count = val_date_df.sort_values(['VAL_YEAR', 'VAL_MONTH', 'PHONE_STATUS1']).groupby(['VAL_YEAR', 
                                        'VAL_MONTH', 'PHONE_STATUS1']).size().reset_index()
month_phone_count = month_phone_count.rename(columns = {0:'count'})

month_addr_count = val_date_df.sort_values(['VAL_YEAR', 'VAL_MONTH', 'ADDRESS_STATUS1']).groupby(['VAL_YEAR', 
                                        'VAL_MONTH', 'ADDRESS_STATUS1']).size().reset_index()
month_addr_count = month_addr_count.rename(columns = {0:'count'})

month_known_bad_count = known_bad_df.sort_values(['VAL_YEAR', 'VAL_MONTH', 'RESULT_OF_CALL']).groupby(['VAL_YEAR', 
                                        'VAL_MONTH', 'RESULT_OF_CALL']).size().reset_index()
month_known_bad_count = month_known_bad_count.rename(columns = {0:'count'})


print('----------------------')
print('Validation Information')
print('----------------------')
print('Number of validation samples received: {}'.format(val_results_df.shape[0]))
print('\n')

print('-----------------')
print('All Phone Results')
print('-----------------')
print(all_phone_count)
print('\n')

print('-----------------------')
print('All Known Bad Phone Results')
print('-----------------------')
print(all_known_bad_count)
print('\n')

print('-------------------')
print('All Address Results')
print('-------------------')
print(all_addr_count)
print('\n')

# Save count dataframes to output analysis file
writer = pd.ExcelWriter(anlys_out_file, engine = 'xlsxwriter')
all_phone_count.to_excel(writer, sheet_name = 'all_phone_cnts', index = False, header = True)
month_phone_count.to_excel(writer, sheet_name = 'month_phone_cnts', index = False, header = True)
all_addr_count.to_excel(writer, sheet_name = 'all_addr_count', index = False, header = True)
month_addr_count.to_excel(writer, sheet_name = 'month_addr_cnts', index = False, header = True)
all_known_bad_count.to_excel(writer, sheet_name = 'all_known_bad_count', index = False, header = True)
month_known_bad_count.to_excel(writer, sheet_name = 'month_known_bad_cnts', index = False, header = True)
writer.save()

known_bad_batch = create_phone_delete(known_bad_df, 'ME_NO', 'OFFICE_PHONE')

known_bad_df.to_csv(kb_del_all_out_file, index = False, header = True)
known_bad_batch.to_csv(kb_del_out_file, index = False, header = True)


val_ppd_df = val_results_df.merge(ppd_df, how = 'inner', left_on = ['ME_NO', 'OFFICE_PHONE'], 
                                  right_on = ['ME', 'TELEPHONE_NUMBER'])

# Create dataframe with data required for the update new number add batch job
updated_phone_df = val_ppd_df[val_ppd_df['CAPTURED_NUMBER'].notnull()]

if str(updated_phone_df['ME_NO'].dtypes) == 'int' or str(updated_phone_df['ME_NO'].dtypes) == 'int64':
    updated_phone_df['ME_NO'] =  updated_phone_df['ME_NO'].apply(lambda x: '{0:0>11}'.format(x))
    
updated_add_batch = create_phone_replace(updated_phone_df, 'ME_NO', 'CAPTURED_NUMBER', phone_source)
updated_add_batch.to_csv(up_add_out_file, index = None, header = True)

# Save all data for updated cases
updated_phone_df.to_csv(up_all_out_file, index = None, header = True)

# change logging back to console and close log file
sys.stdout = old_stdout
log_file.close()



