# Kari Palmier    Created 8/8/19
# Kari Palmier    Updated to filter known bad by if they are in current PPD
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
from get_input_date_range import get_input_date_range
from get_aims_db_tables import get_ent_comm_phones
from select_files import select_files
from combine_data import combine_data
import datalabs.curate.dataframe as df
from get_entity_ppd_info import create_ent_me_data, clean_phn_data
from datalabs.access.aims import AIMS

warnings.filterwarnings("ignore")

    
root = tk.Tk()
root.withdraw()

init_wslive_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\WSLive\\'
init_anlys_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\WSLive\\Analysis\\'

db_str = input('Select csv files with AIMS data? ([y]/n): ')
db_str = db_str.lower()
if db_str.find('n') < 0:
    db_str = 'y'

if db_str.find('y') < 0:
    # Get files needed
    ddb_info_file = filedialog.askopenfilename(initialdir="C:\\",
                                               title="Choose txt file with database login information...")
else:
    init_ent_comm_dir = 'C:\\'
    ent_comm_file = filedialog.askopenfilename(initialdir=init_ent_comm_dir,
                                               title="Choose the entity_comm_at data csv file...")

    ent_key_file = filedialog.askopenfilename(title="Choose the entity_key_et data csv file...")
    
    phone_file = filedialog.askopenfilename(title="Choose the phone_at data csv file...")

    

wslive_results_file = filedialog.askopenfilename(initialdir=init_wslive_dir,
                                                 title="Choose WSLive file with results encoded...")

init_sample_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Survey_Samples\\'
sample_paths = select_files(init_sample_dir, 'Select sample file(s) sent corresponding to results')

anlys_out_dir = filedialog.askdirectory(initialdir=init_anlys_dir,
                                        title="Choose directory to save analysis output...")
anlys_out_dir = anlys_out_dir.replace("/", "\\")
anlys_out_dir += "\\"


start_date, end_date, date_range_str = get_input_date_range()


anlys_base_name = anlys_out_dir + date_range_str + '_'
count_end_name = '_WSLive_MF_Source_Counts.xlsx'

old_stdout = sys.stdout
log_filename = anlys_out_dir + date_range_str + '_WSLive_MF_Source_Analysis_Log.txt'
log_file = open(log_filename, "w")
sys.stdout = log_file

if db_str.find('y') < 0:
    with AIMS() as aims:
        # get entity_comm_at, phone_at, and me info for latest begin date of each me/entity_id
        entity_comm_me_df = get_ent_comm_phones(aims._connection)
else:
    # Load entity data
    ent_comm_df = pd.read_csv(ent_comm_file, delimiter=",", index_col=None, header=0, dtype=str)
    ent_comm_df = ent_comm_df[ent_comm_df['comm_cat'] == 'P']
    
    ent_key_df = pd.read_csv(ent_key_file, delimiter = ",", index_col = None, header = 0, dtype = str)    
    ent_key_df = create_ent_me_data(ent_key_df)
    entity_comm_me_df = entity_comm_me_df.rename(columns = {'ent_me':'me'})
    
    entity_comm_me_df = ent_comm_df.merge(ent_key_df['entity_id', 'me'], how = 'inner', on = 'entity_id')

    phone_df = pd.read_csv(phone_file, delimiter = ",", index_col = None, header = 0, dtype = str)
    phone_df = clean_phn_data(phone_df)
    phone_df = phone_df.rename(columns = {'phn_comm_id':'comm_id'})
    
    entity_comm_me_df = entity_comm_me_df.merge(phone_df['comm_id', 'aims_phone'], how = 'inner', on = 'comm_id')
    
    

entity_comm_uniq_df = entity_comm_me_df.sort_values(['begin_dt'], ascending = False).groupby(['me', 
                                                'aims_phone']).first().reset_index()

# Read in samples sent
sample_df = combine_data(sample_paths, None, 0)
sample_df = df.rename_in_upper_case(sample_df)

# Read in wslive data
wslive_results_df = pd.read_csv(wslive_results_file, delimiter=",", index_col=None, header=0, dtype=str)
wslive_results_df = df.rename_in_upper_case(wslive_results_df)

# Join results with sample sent on ME
wslive_res_smpl_df = wslive_results_df.merge(sample_df, how='inner', left_on='PHYSICIAN_ME_NUMBER',
                                             right_on='ME')
# Get data for date range specified
wslive_res_smpl_df['WSLIVE_FILE_DT'] = pd.to_datetime(wslive_res_smpl_df['WSLIVE_FILE_DT'])
wslive_date_df = wslive_res_smpl_df[(wslive_res_smpl_df['WSLIVE_FILE_DT'] >= start_date) &
                                    (wslive_res_smpl_df['WSLIVE_FILE_DT'] <= end_date)]
            
# If source type for MF is a list so need to treat differently
source_code = ['C', 'Z', 'CR', 'CA', 'CB']
source_name = 'MF'
wslive_source_df = wslive_date_df[wslive_date_df['SOURCE'].isin(source_code)]

wslive_ent_df = wslive_source_df.merge(entity_comm_uniq_df,
                                       how='inner',
                                       left_on=['PHYSICIAN_ME_NUMBER', 'OFFICE_TELEPHONE'],
                                       right_on=['me', 'aims_phone'])

status_vars = ['PHONE_STATUS']    
     
for var in status_vars:   
    
    # Report analysis summaries for each phone entry type
    print('\n')
    print('--------------------------------------------------------------')
    print('WSLive Masterfile {} Analysis'.format(var.upper()))
    print('--------------------------------------------------------------')
    
     # Save count dataframes to output analysis file
    anlys_out_file = anlys_base_name + var.upper() + count_end_name
    writer = pd.ExcelWriter(anlys_out_file, engine='xlsxwriter')
    
    result_types = wslive_ent_df[var].unique()

    for result in result_types:
        temp_df = wslive_ent_df[wslive_ent_df[var] == result]
        
        source_counts = temp_df.sort_values(['src_cat_code']).groupby(['src_cat_code']).size().reset_index()
        source_counts = source_counts.rename(columns = {0:'count'})
        source_counts = source_counts.sort_values('count', ascending = False)
        
        month_source_counts = temp_df.sort_values(['WS_YEAR',
                                                   'WS_MONTH',
                                                   'src_cat_code']).groupby(['WS_YEAR',
                                                                             'WS_MONTH',
                                                                             'src_cat_code']).size().reset_index()
        month_source_counts = month_source_counts.rename(columns={0: 'count'})
        month_source_counts = month_source_counts.sort_values(['WS_YEAR', 'WS_MONTH', 'count'], ascending=False)
        
        num_rows = source_counts.shape[0] + 1
        num_cols = source_counts.shape[1] + 1
        pd.set_option('max_rows', num_rows)
        pd.set_option('max_columns', num_cols)

        print('\n')
        print('{} Source Counts'.format(result))
        print('--------------------------------------------------')
        print(source_counts)
        
        source_counts.to_excel(writer, sheet_name=result, index=False, header=True)
        
        month_sheet = result + ' - Monthly'
        month_source_counts.to_excel(writer, sheet_name=month_sheet, index=False, header=True)

    temp_df = wslive_ent_df[wslive_ent_df[var] == 'Known Bad']
    kb_types = temp_df['COMMENTS'].unique()
    
    for kb_type in kb_types:
        
        kb_df = temp_df[temp_df['COMMENTS'] == kb_type]
        
        kb_source_counts = kb_df.sort_values(['src_cat_code']).groupby(['src_cat_code']).size().reset_index()
        kb_source_counts = kb_source_counts.rename(columns={0: 'count'})
        
        month_kb_source_counts = kb_df.sort_values(['WS_YEAR',
                                                    'WS_MONTH',
                                                    'src_cat_code']).groupby(['WS_YEAR',
                                                                              'WS_MONTH',
                                                                              'src_cat_code']).size().reset_index()
        month_kb_source_counts = month_kb_source_counts.rename(columns={0: 'count'})
        
        print('\n')
        print('Known Bad {} Source Counts'.format(kb_type))
        print('--------------------------------------------------')
        print(kb_source_counts)
        
        kb_sheet = 'KB ' + kb_type 
        kb_sheet = kb_sheet.replace(',', '')
        if len(kb_sheet) > 31:
            kb_sheet = kb_sheet[:31].strip()
        kb_source_counts.to_excel(writer, sheet_name=kb_sheet, index=False, header=True)
        
        month_kb_sheet = 'KB ' + kb_type + ' Monthly'
        month_kb_sheet = month_kb_sheet.replace(',', '')
        if len(month_kb_sheet) > 31:
            month_kb_sheet = month_kb_sheet[:(31 - len(' Monthly'))].strip() + ' Monthly'
        month_kb_source_counts.to_excel(writer, sheet_name=month_kb_sheet, index=False, header=True)
    
        
    writer.save()
        
# change logging back to console and close log file
sys.stdout = old_stdout
log_file.close()

