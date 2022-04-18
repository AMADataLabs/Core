# Kari Palmier    Created 8/26/19
#
#############################################################################
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os

import warnings
warnings.filterwarnings("ignore")


root = tk.Tk()
root.withdraw()

init_val_dir = 'U:\\Source Files\\Data Release\\Sandbox\\WSLive Validation Returns\\'
val_results_file = filedialog.askopenfilename(initialdir = init_val_dir,
                                         title = "Choose validation file to encode with results...")

init_val_out_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Validation\\'

val_combined_file = filedialog.askopenfilename(initialdir = init_val_out_dir,
                                         title = "Choose the combined validation results file (cancel will make new file)...")


val_out_dir = filedialog.askdirectory(initialdir = init_val_out_dir,
                                         title = "Choose directory to save validation with results output...")
val_out_dir = val_out_dir.replace("/", "\\")
val_out_dir += "\\"

archive_dir = val_out_dir + '_Archived\\'
if not os.path.exists(archive_dir):
    os.mkdir(archive_dir)


start_ndx = val_results_file.find('VALIDATIONS_RETURN_')
start_ndx = start_ndx + len('VALIDATIONS_RETURN_')
end_ndx = val_results_file.find('.')
val_date_str = val_results_file[start_ndx:end_ndx]

temp_xl = pd.ExcelFile(val_results_file)

sheet_names = temp_xl.sheet_names  # see all sheet names

for i in range(len(sheet_names)):
    
    temp_sheet = sheet_names[i]
    temp_df = pd.read_excel(val_results_file, sheet_name = temp_sheet, index_col = None, header = 0, dtype = str)
    
    temp_df['LASTCALL'] = pd.to_datetime(temp_df['LASTCALL'])
    temp_df['VAL_MONTH'] = temp_df['LASTCALL'].apply(lambda x: x.month if x != None else x) 
    temp_df['VAL_YEAR'] = temp_df['LASTCALL'].apply(lambda x: x.year if x != None else x)
    
    for col in list(temp_df.columns.values):
        temp_df[col] = temp_df[col].apply(lambda x: x.upper() if isinstance(x, str) else x)
    
    temp_df['PHONE_STATUS1'] = 'Inconclusive'
    temp_df['ADDRESS_STATUS1'] = 'Inconclusive'
    
    if i == 0 or i == 1:
        
        phone_confirm_ndx = (temp_df['RESULT_OF_CALL'] == 'COMPLETE') & (temp_df['CORRECT_PHONE'] == 'Y')
        phone_update_ndx = (temp_df['RESULT_OF_CALL'] == 'COMPLETE') & ((temp_df['CORRECT_PHONE'] == 'N') | \
                      (temp_df['CORRECT_PHONE'].isna())) & (temp_df['CAPTURED_NUMBER'].notnull())
        phone_kb_ndx = temp_df['RESULT_OF_CALL'].isin(['DISCONNECT', 'DISCONNECTED', 'WRONG PHONE NUMBER', 
                              'WRONG NUMBER', 'NOT IN SERVICE'])
        
        temp_df.loc[phone_confirm_ndx, 'PHONE_STATUS1'] = 'Confirm'
        temp_df.loc[phone_update_ndx, 'PHONE_STATUS1'] = 'Update'
        temp_df.loc[phone_kb_ndx, 'PHONE_STATUS1'] = 'Known Bad'
        
        
        addr_confirm_ndx = (temp_df['RESULT_OF_CALL'] == 'COMPLETE') & (temp_df['CORRECT_ADDRESS'] == 'Y')
        addr_update_ndx = (temp_df['RESULT_OF_CALL'] == 'COMPLETE') & ((temp_df['CORRECT_ADDRESS'] == 'N') | \
                      (temp_df['CORRECT_ADDRESS'].isna())) & (temp_df['CAPTURED_ADD2'].notnull())
        addr_kb_ndx = temp_df['RESULT_OF_CALL'].isin(['DISCONNECT', 'DISCONNECTED', 'WRONG PHONE NUMBER', 
                             'WRONG NUMBER', 'NOT IN SERVICE'])
        
        temp_df.loc[addr_confirm_ndx, 'ADDRESS_STATUS1'] = 'Confirm'
        temp_df.loc[addr_update_ndx, 'ADDRESS_STATUS1'] = 'Update'
        temp_df.loc[addr_kb_ndx, 'ADDRESS_STATUS1'] = 'Known Bad'
        
    elif i == 2:
        
        phone_kb_ndx = temp_df['RESULT_OF_CALL'].isin(['DISCONNECT', 'DISCONNECTED', 'WRONG PHONE NUMBER', 
                             'WRONG NUMBER', 'NOT IN SERVICE'])
        temp_df.loc[phone_kb_ndx, 'PHONE_STATUS1'] = 'Known Bad'
        
        addr_kb_ndx = temp_df['RESULT_OF_CALL'].isin(['DISCONNECT', 'DISCONNECTED', 'WRONG PHONE NUMBER', 
                             'WRONG NUMBER', 'NOT IN SERVICE'])
        temp_df.loc[addr_kb_ndx, 'ADDRESS_STATUS1'] = 'Known Bad'
       
    else:
        
        temp_df['PHONE_STATUS1'] = 'No Contact'
        temp_df['ADDRESS_STATUS1'] = 'No Contact'
        
    if i == 0:
        comb_month_df = temp_df[:]
    else:
        comb_month_df = pd.concat([comb_month_df, temp_df], axis = 0, ignore_index = True)
        
        
val_month_out_file = val_out_dir + 'val_returns_with_results_' + val_date_str + '.csv'
comb_month_df.to_csv(val_month_out_file, index = None, header = True)      


if val_combined_file == '':
    combined_val_df = comb_month_df[:]
    
else:    
    temp_comb_df = pd.read_csv(val_combined_file, delimiter = ",", index_col = None, header = 0, dtype = str)

    combined_val_df = pd.concat([temp_comb_df, comb_month_df], axis = 0, ignore_index = True)
    
    
combined_val_df['VAL_MONTH'] = combined_val_df['VAL_MONTH'].astype('str')
combined_val_df['VAL_YEAR'] = combined_val_df['VAL_YEAR'].astype('str')
combined_val_df['month_yr'] = combined_val_df['VAL_MONTH'] + combined_val_df['VAL_YEAR']
combined_val_df['month_yr'] = pd.to_datetime(combined_val_df['month_yr'], format = '%m%Y')
    
min_date = combined_val_df['month_yr'].min()
min_time_str = min_date.strftime("%Y-%m")

max_date = combined_val_df['month_yr'].max()
max_time_str = max_date.strftime("%Y-%m")
         
combined_val_df = combined_val_df.drop(['month_yr'], axis = 1)

combined_out_file = val_out_dir + 'val_returns_with_results_combined.csv'
combined_val_df.to_csv(combined_out_file, index = None, header = True)      

combined_arch_out_file = archive_dir + 'val_returns_with_results_combined_' + min_time_str + '_to_' + max_time_str + '.csv'
combined_val_df.to_csv(combined_arch_out_file, index = None, header = True)      

   
    
    
    