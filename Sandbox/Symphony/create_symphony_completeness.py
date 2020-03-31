# Kari Palmier    9/9/19    Created
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

from get_ddb_logins import get_ddb_logins
from get_ods_db_tables import get_symphony_all_phys_info, get_ods_connection
from get_comp_completeness import get_var_completeness, get_ppd_comp_comparison
import datalabs.curate.dataframe as df

import warnings
warnings.filterwarnings("ignore")


root = tk.Tk()
root.withdraw()

data_sel = input('Select existing Symphony data csv file? (y/[n]): ')
if data_sel.lower().find('y') < 0:
    data_sel = 'n'

    # Get files needed
    ddb_info_file = filedialog.askopenfilename(initialdir = "C:\\",
                                             title = "Choose txt file with database login information...")
else:
    sym_file = filedialog.askopenfilename(initialdir = "U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Symphony\\",
                                             title = "Choose the Symphony data csv file...")
    
# Get model file needed
ppd_file = filedialog.askopenfilename(initialdir = "U:\\Source Files\\Data Analytics\\Data-Science\\Data\\PPD\\",
                                         title = "Choose the latest PPD file...")

init_save_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Symphony\\Analysis\\'
out_dir = filedialog.askdirectory(initialdir = init_save_dir,
                                         title = "Choose directory to analysis output in...")
out_dir = out_dir.replace("/", "\\")
out_dir += "\\"

current_time = datetime.datetime.now()
start_time_str = current_time.strftime("%Y-%m-%d")

# Create log file
old_stdout = sys.stdout
log_filename = out_dir + start_time_str + '_Symphony_Completeness_Analysis_Log' + '.txt'
log_file = open(log_filename, "w")
sys.stdout = log_file

if data_sel == 'n':
    # Get ddb login information
    ddb_login_dict = get_ddb_logins(ddb_info_file)

    if 'ODS' not in ddb_login_dict.keys():
        print('ODS login information not present.')
        sys.exit()

    ODS_conn = get_ods_connection(ddb_login_dict['ODS']['username'], ddb_login_dict['ODS']['password'])
    
    sym_df = get_symphony_all_phys_info(ODS_conn)
    
    ODS_conn.close()
    
else:
    sym_df =  pd.read_csv(sym_file, delimiter = ",", index_col = None, header = 0, dtype = str)

sym_df = df.rename_in_upper_case(sym_df)
sym_df = df.upper_values(sym_df)
    
ppd_df =  pd.read_csv(ppd_file, delimiter = ",", index_col = None, header = 0, dtype = str)
ppd_df = df.rename_in_upper_case(ppd_df)
ppd_df = df.upper_values(ppd_df)

ppd_df['ME_SUBSTR'] = ppd_df['ME'].apply(lambda x: x[:(len(x) - 1)])

ppd_dpc_df = ppd_df[ppd_df['TOP_CD'] == '020']

ppd_join_var = 'ME_SUBSTR'
comp_join_var = 'SYM_ME'

print('------------------------------------')
print('------------------------------------')
print('PPD/Symphony Overall Data Comparison')
print('------------------------------------')
print('------------------------------------')
print('\n')

ppd_comp_df = get_ppd_comp_comparison(sym_df, ppd_df, ppd_join_var, comp_join_var, 'Symphony')

compare_save_file = out_dir + start_time_str + '_Symphony_PPD_Comparison_Analysis.xlsx'
compare_writer = pd.ExcelWriter(compare_save_file, engine = 'xlsxwriter')
ppd_comp_df.to_excel(compare_writer, sheet_name = 'sym_ppd_comparison', index = True, header = True)    
compare_writer.save()

sym_var_names = ['SYM_TELEPHONE_NUMBER', 'SYM_FAX_NUMBER', ['SYM_POLO_MAILING_LINE_2', 
                   'SYM_POLO_CITY', 'SYM_POLO_STATE', 'SYM_POLO_ZIP'], 'SYM_POLO_MAILING_LINE_2', 
                   'SYM_POLO_CITY', 'SYM_POLO_STATE', 'SYM_POLO_ZIP']
ppd_var_names = ['TELEPHONE_NUMBER', 'FAX_NUMBER', ['POLO_MAILING_LINE_2', 
                   'POLO_CITY', 'POLO_STATE', 'POLO_ZIP'], 'POLO_MAILING_LINE_2', 
                   'POLO_CITY', 'POLO_STATE', 'POLO_ZIP']

all_save_file = out_dir + start_time_str + '_Symphony_All_Completeness_Analysis.xlsx'
all_writer = pd.ExcelWriter(all_save_file, engine = 'xlsxwriter')

print('-------------------------------------------')
print('-------------------------------------------')
print('PPD/Symphony Variable Comparison - All Data')
print('-------------------------------------------')
print('-------------------------------------------')
print('The following results include all physicians, not just PPD DPC.')
print('\n')

for i in range(len(sym_var_names)):
    
    total_complete_df = get_var_completeness(sym_df, ppd_df, sym_var_names[i], 
                                              ppd_var_names[i], ppd_join_var, comp_join_var, 'Symphony')

    if isinstance(ppd_var_names[i], list):
        save_var = 'TOTAL_ADDRESS'
    else:
        save_var = ppd_var_names[i]
        
    total_complete_df.to_excel(all_writer, sheet_name = save_var, index = True, header = True)
    
all_writer.save()


dpc_save_file = out_dir + start_time_str + '_Symphony_DPC_Completeness_Analysis.xlsx'
dpc_writer = pd.ExcelWriter(dpc_save_file, engine = 'xlsxwriter')

print('-----------------------------------------------')
print('-----------------------------------------------')
print('PPD/Symphony Variable Comparison - PPD DPC Only')
print('-----------------------------------------------')
print('-----------------------------------------------')
print('The following results includes only physicians marked as DPC in the PPD.')
print('\n')

for i in range(len(sym_var_names)):
    
    dpc_complete_df = get_var_completeness(sym_df, ppd_dpc_df, sym_var_names[i], 
                                              ppd_var_names[i], ppd_join_var, comp_join_var, 'Symphony')
    
    if isinstance(ppd_var_names[i], list):
        dpc_save_var = 'TOTAL_ADDRESS'
    else:
        dpc_save_var = ppd_var_names[i]
        
    dpc_complete_df.to_excel(dpc_writer, sheet_name = dpc_save_var, index = True, header = True)
    
dpc_writer.save()

# change logging back to console and close log file
sys.stdout = old_stdout
log_file.close()
