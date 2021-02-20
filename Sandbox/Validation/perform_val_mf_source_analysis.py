# Kari Palmier    Created 8/27/19
# Kari Palmier    Updated to filter known bad by if they are in current PPD
#
#############################################################################
import argparse
import datetime
import os
import sys
import tkinter as tk
from tkinter import filedialog

import pandas as pd

import settings
from get_aims_db_tables import get_ent_comm_phones
from get_entity_ppd_info import create_ent_me_data, clean_phn_data
from datalabs.access.aims import AIMS
import datalabs.util.datetime as dt


def main(args):
    root = tk.Tk()
    root.withdraw()

    init_val_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Validation\\'
    init_anlys_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Validation\\Analysis\\'

    db_str = input('Select csv files with AIMS data? ([y]/n): ')
    db_str = db_str.lower()
    if db_str.find('n') < 0:
        db_str = 'y'

    if db_str.find('y') < 0:
        # Get files needed
        ddb_info_file = filedialog.askopenfilename(initialdir = "C:\\",
                                                 title = "Choose txt file with database login information...")
    else:
        init_ent_comm_dir = 'C:\\'
        ent_comm_file = filedialog.askopenfilename(initialdir = init_ent_comm_dir,
                                                 title = \
                                                 "Choose the entity_comm_at data csv file...")

        ent_key_file = filedialog.askopenfilename(title = \
                                                    "Choose the entity_key_et data csv file...")

        phone_file = filedialog.askopenfilename(title = \
                                                    "Choose the phone_at data csv file...")


    val_results_file = filedialog.askopenfilename(initialdir = init_val_dir,
                                             title = "Choose validation file with results encoded...")

    anlys_out_dir = filedialog.askdirectory(initialdir = init_anlys_dir,
                                             title = "Choose directory to save analysis output...")
    anlys_out_dir = anlys_out_dir.replace("/", "\\")
    anlys_out_dir += "\\"


    current_time = datetime.datetime.now()
    start_time_str = current_time.strftime("%Y-%m-%d")

    time_str = input('Do you want to choose a time subset (n will use all data)? (y/[n]): ')

    if time_str.lower().find('y') < 0:
        date_range_str = ''
    else:
        start_date, end_date, date_range_str = dt.date_range(args['start-date'], args['end-date'])


    # Read in wslive data
    val_results_df = pd.read_csv(val_results_file, delimiter = ",", index_col = None, header = 0, dtype = str)

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

    log_filename = anlys_out_dir + date_range_str + '_Val_MF_Source_Analysis_Log.txt'
    anlys_base_name = anlys_out_dir + date_range_str + '_'
    count_end_name = '_Val_MF_Source_Counts.xlsx'


    old_stdout = sys.stdout
    log_file = open(log_filename, "w")
    sys.stdout = log_file

    if db_str.find('y') < 0:
        with AIMS() as aims:
            # get entity_comm_at, phone_at, and me info for latest begin date of each me/entity_id
            entity_comm_me_df = get_ent_comm_phones(aims._connection)
    else:
        # Load entity data
        ent_comm_df = pd.read_csv(ent_comm_file, delimiter = ",", index_col = None, header = 0, dtype = str)
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

               
    # If source type for MF is a list so need to treat differently
    val_ent_df = val_date_df.merge(entity_comm_uniq_df, how = 'inner', 
                                          left_on = ['ME_NO', 'OFFICE_PHONE'],
                                          right_on = ['me', 'aims_phone'])

    status_vars = ['PHONE_STATUS1']
         
    for var in status_vars:   
        
        # Report analysis summaries for each phone entry type
        print('\n')
        print('--------------------------------------------------------------')
        print('Validation Masterfile {} Analysis'.format(var.upper()))
        print('--------------------------------------------------------------')
        
         # Save count dataframes to output analysis file
        anlys_out_file = anlys_base_name + var.upper() + count_end_name
        writer = pd.ExcelWriter(anlys_out_file, engine = 'xlsxwriter')
        
        result_types = val_ent_df[var].unique()

        for result in result_types:
            temp_df = val_ent_df[val_ent_df[var] == result]
            
            source_counts = temp_df.sort_values(['src_cat_code']).groupby(['src_cat_code']).size().reset_index()
            source_counts = source_counts.rename(columns = {0:'count'})
            source_counts = source_counts.sort_values('count', ascending = False)
            
            month_source_counts = temp_df.sort_values(['VAL_YEAR', 'VAL_MONTH', 'src_cat_code']).groupby(['VAL_YEAR', 
                                               'VAL_MONTH', 'src_cat_code']).size().reset_index()
            month_source_counts = month_source_counts.rename(columns = {0:'count'})
            month_source_counts = month_source_counts.sort_values(['VAL_YEAR', 'VAL_MONTH', 'count'], ascending = False)
            
            num_rows = source_counts.shape[0] + 1
            num_cols = source_counts.shape[1] + 1
            pd.set_option('max_rows', num_rows)
            pd.set_option('max_columns', num_cols)

            print('\n')
            print('{} Source Counts'.format(result))
            print('----------------------------------------')
            print(source_counts)
            
            source_counts.to_excel(writer, sheet_name = result, index = False, header = True)
            
            month_sheet = result + '- Monthly'
            month_source_counts.to_excel(writer, sheet_name = month_sheet, index = False, header = True)
            
            if result == 'Known Bad':
                
                kb_types = temp_df['RESULT_OF_CALL'].unique()
                
                for kb_type in kb_types:
                    
                    kb_df = temp_df[temp_df['RESULT_OF_CALL'] == kb_type]
                    
                    kb_source_counts = kb_df.sort_values(['src_cat_code']).groupby(['src_cat_code']).size().reset_index()
                    kb_source_counts = kb_source_counts.rename(columns = {0:'count'})
                    
                    month_kb_source_counts = kb_df.sort_values(['VAL_YEAR', 'VAL_MONTH', 'src_cat_code']).groupby(['VAL_YEAR', 
                                                        'VAL_MONTH', 'src_cat_code']).size().reset_index()
                    month_kb_source_counts = month_kb_source_counts.rename(columns = {0:'count'})
                    
                    print('\n')
                    print('Known Bad {} Source Counts'.format(kb_type))
                    print('--------------------------------------------------')
                    print(kb_source_counts)
                    
                    kb_sheet = 'KB ' + kb_type 
                    kb_sheet = kb_sheet.replace(',', '')
                    if len(kb_sheet) > 31:
                        kb_sheet = kb_sheet[:31].strip()
                    kb_source_counts.to_excel(writer, sheet_name = kb_sheet, index = False, header = True)
                    
                    month_kb_sheet = 'KB ' + kb_type + ' Monthly'
                    month_kb_sheet = month_kb_sheet.replace(',', '')
                    if len(month_kb_sheet) > 31:
                        month_kb_sheet = month_kb_sheet[:(31 - len(' Monthly'))].strip() + ' Monthly'
                    month_kb_source_counts.to_excel(writer, sheet_name = month_kb_sheet, index = False, header = True)
            
            
        writer.save()
            
    # change logging back to console and close log file
    sys.stdout = old_stdout
    log_file.close()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-s', '--start-date', required=True,
                    help='WSLive data start date in the form YYYY-MM[-DD] (default day is 1).')
    ap.add_argument('-e', '--end-date', required=True,
                    help='WSLive data end date in the form YYYY-MM[-DD] (default day is last day of month).')
    args = vars(ap.parse_args())

    main(args)

