# Kari Palmier    9/9/19    Created
#
#############################################################################
import datetime
import os
import sys
import tkinter as tk
from tkinter import filedialog

import pandas as pd

import settings
from get_ods_db_tables import get_symphony_all_phys_info, get_iqvia_all_phys_info
from get_comp_completeness import get_var_completeness, get_ppd_comp_comparison

from   datalabs.access.ods import ODS
import datalabs.curate.dataframe  # pylint: disable=unused-import


root = tk.Tk()
root.withdraw()

data_sel = input('Select existing competitor data csv files? (y/[n]): ')
if data_sel.lower().find('y') < 0:
    data_sel = 'n'

    # Get files needed
    ddb_info_file = filedialog.askopenfilename(initialdir = "C:\\",
                                             title = "Choose txt file with database login information...")
else:
    iq_file = filedialog.askopenfilename(initialdir = "U:\\Source Files\\Data Analytics\\Data-Science\\Data\\IQVIA\\",
                                             title = "Choose the IQVIA data csv file...")

    sym_file = filedialog.askopenfilename(initialdir = "U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Symphony\\",
                                             title = "Choose the Symphony data csv file...")
    
# Get model file needed
ppd_file = filedialog.askopenfilename(initialdir = "U:\\Source Files\\Data Analytics\\Data-Science\\Data\\PPD\\",
                                         title = "Choose the latest PPD file...")

init_save_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\PPD\\Analysis\\'
out_dir = filedialog.askdirectory(initialdir = init_save_dir,
                                         title = "Choose directory to analysis output in...")
out_dir = out_dir.replace("/", "\\")
out_dir += "\\"

current_time = datetime.datetime.now()
start_time_str = current_time.strftime("%Y-%m-%d")

# Create log file
old_stdout = sys.stdout
log_filename = out_dir + start_time_str + '_Common_Completeness_Analysis_Log' + '.txt'
log_file = open(log_filename, "w")
sys.stdout = log_file

if data_sel == 'n':
    with ODS() as ods:
        iqvia_df = get_iqvia_all_phys_info(ODS_conn)
        
        sym_df = get_symphony_all_phys_info(ODS_conn)
else:
    iqvia_df =  pd.read_csv(iq_file, delimiter = ",", index_col = None, header = 0, dtype = str)

    sym_df =  pd.read_csv(sym_file, delimiter = ",", index_col = None, header = 0, dtype = str)

iqvia_df = iqvia_df.datalabs.rename_in_upper_case()
iqvia_df = iqvia_df.datalabs.upper()

sym_df = sym_df.datalabs.rename_in_upper_case()
sym_df = sym_df.datalabs.upper()
    
ppd_df =  pd.read_csv(ppd_file, delimiter = ",", index_col = None, header = 0, dtype = str)
ppd_df = ppd_df.datalabs.rename_in_upper_case()
ppd_df = ppd_df.datalabs.upper()

ppd_df['ME_SUBSTR'] = ppd_df['ME'].apply(lambda x: x[:(len(x) - 1)])

ppd_dpc_df = ppd_df[ppd_df['TOP_CD'] == '020']

ppd_join_var = 'ME_SUBSTR'
iq_join_var = 'IMS_ME'
sym_join_var = 'SYM_ME'

ppd_me_subs = ppd_df[ppd_join_var]
iq_me_subs = iqvia_df[iq_join_var]
sym_me_subs = sym_df[sym_join_var]

ppd_iq_me_subs = set(ppd_me_subs).intersection(set(iq_me_subs))
common_me_subs = list(ppd_iq_me_subs.intersection(set(sym_me_subs)))

ppd_common_df = ppd_df[ppd_df[ppd_join_var].isin(common_me_subs)]
iqvia_common_df = iqvia_df[iqvia_df[iq_join_var].isin(common_me_subs)]
sym_common_df = sym_df[sym_df[sym_join_var].isin(common_me_subs)]

ppd_dpc_me_subs = ppd_dpc_df[ppd_join_var]
common_dpc_me_subs = list(set(common_me_subs).intersection(set(ppd_dpc_me_subs)))

ppd_dpc_common_df = ppd_dpc_df[ppd_dpc_df[ppd_join_var].isin(common_dpc_me_subs)]
iqvia_dpc_common_df = iqvia_common_df[iqvia_common_df[iq_join_var].isin(common_dpc_me_subs)]
sym_dpc_common_df = sym_common_df[sym_common_df[sym_join_var].isin(common_dpc_me_subs)]

iqvia_var_names = ['IMS_TELEPHONE_NUMBER', 'IMS_FAX_NUMBER', ['IMS_POLO_MAILING_LINE_2', 
                   'IMS_POLO_CITY', 'IMS_POLO_STATE', 'IMS_POLO_ZIP'], 'IMS_POLO_MAILING_LINE_2', 
                   'IMS_POLO_CITY', 'IMS_POLO_STATE', 'IMS_POLO_ZIP']
sym_var_names = ['SYM_TELEPHONE_NUMBER', 'SYM_FAX_NUMBER', ['SYM_POLO_MAILING_LINE_2', 
                   'SYM_POLO_CITY', 'SYM_POLO_STATE', 'SYM_POLO_ZIP'], 'SYM_POLO_MAILING_LINE_2', 
                   'SYM_POLO_CITY', 'SYM_POLO_STATE', 'SYM_POLO_ZIP']
ppd_var_names = ['TELEPHONE_NUMBER', 'FAX_NUMBER', ['POLO_MAILING_LINE_2', 
                   'POLO_CITY', 'POLO_STATE', 'POLO_ZIP'], 'POLO_MAILING_LINE_2', 
                   'POLO_CITY', 'POLO_STATE', 'POLO_ZIP']

comp_names = ['IQVIA', 'Symphony']

for comp_name in comp_names:
    
    if comp_name == 'IQVIA':
        comp_join_var = iq_join_var
        comp_df = iqvia_common_df
        comp_dpc_df = iqvia_dpc_common_df
        comp_var_names = iqvia_var_names
    elif comp_name == 'Symphony':
        comp_join_var = sym_join_var
        comp_df = sym_common_df
        comp_dpc_df = sym_dpc_common_df
        comp_var_names = sym_var_names
    
    
    print('------------------------------------')
    print('------------------------------------')
    print('PPD/{} Overall Data Comparison'.format(comp_name))
    print('------------------------------------')
    print('------------------------------------')
    print('\n')
    
    ppd_comp_df = get_ppd_comp_comparison(comp_df, ppd_common_df, ppd_join_var, comp_join_var, comp_name)
    
    compare_save_file = out_dir + start_time_str + '_Common_' + comp_name + '_PPD_Comparison_Analysis.xlsx'
    compare_writer = pd.ExcelWriter(compare_save_file, engine = 'xlsxwriter')
    ppd_comp_df.to_excel(compare_writer, sheet_name = 'sym_ppd_comparison', index = True, header = True)    
    compare_writer.save()
    
    all_save_file = out_dir + start_time_str + '_Common_' + comp_name + '_All_Completeness_Analysis.xlsx'
    all_writer = pd.ExcelWriter(all_save_file, engine = 'xlsxwriter')
    
    print('-------------------------------------------')
    print('-------------------------------------------')
    print('PPD/{} Variable Comparison - All Data'.format(comp_name))
    print('-------------------------------------------')
    print('-------------------------------------------')
    print('The following results include all physicians, not just PPD DPC.')
    print('\n')
    
    for i in range(len(comp_var_names)):
        
        total_complete_df = get_var_completeness(comp_df, ppd_common_df, comp_var_names[i], 
                                                  ppd_var_names[i], ppd_join_var, comp_join_var, comp_name)
    
        if isinstance(ppd_var_names[i], list):
            save_var = 'TOTAL_ADDRESS'
        else:
            save_var = ppd_var_names[i]
            
        total_complete_df.to_excel(all_writer, sheet_name = save_var, index = True, header = True)
        
    all_writer.save()
    
    
    dpc_save_file = out_dir + start_time_str + '_Common_' + comp_name + '_DPC_Completeness_Analysis.xlsx'
    dpc_writer = pd.ExcelWriter(dpc_save_file, engine = 'xlsxwriter')
    
    print('-----------------------------------------------')
    print('-----------------------------------------------')
    print('PPD/{} Variable Comparison - PPD DPC Only'.format(comp_name))
    print('-----------------------------------------------')
    print('-----------------------------------------------')
    print('The following results includes only physicians marked as DPC in the PPD.')
    print('\n')
    
    ppd_pdc_me_subs = list(ppd_dpc_common_df[ppd_join_var])
    comp_dpc_df = comp_df[comp_df[comp_join_var].isin(ppd_pdc_me_subs)]
    
    for i in range(len(comp_var_names)):
        
        dpc_complete_df = get_var_completeness(comp_dpc_df, ppd_dpc_common_df, comp_var_names[i], 
                                                  ppd_var_names[i], ppd_join_var, comp_join_var, comp_name)
        
        if isinstance(ppd_var_names[i], list):
            dpc_save_var = 'TOTAL_ADDRESS'
        else:
            dpc_save_var = ppd_var_names[i]
            
        dpc_complete_df.to_excel(dpc_writer, sheet_name = dpc_save_var, index = True, header = True)
        
    dpc_writer.save()
    
# change logging back to console and close log file
sys.stdout = old_stdout
log_file.close()
    
