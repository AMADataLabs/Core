# Kari Palmier    8/30/19    Created
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
from get_aims_db_tables import get_comm_usg_preferred_phones, get_ent_comm_phones
from get_entity_ppd_info import set_entity_dates
from rename_entity_cols import rename_comm_cols, rename_usg_cols
from datalabs.access.aims import AIMS
import datalabs.util.datetime as dt

    
def main(args):
  root = tk.Tk()
  root.withdraw()

  init_save_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\WSLive\\Analysis\\'
  out_dir = filedialog.askdirectory(initialdir = init_save_dir,
                                           title = "Choose directory to save output to...")
  out_dir = out_dir.replace("/", "\\")
  out_dir += "\\"

  current_time = datetime.datetime.now()
  start_time_str = current_time.strftime("%Y-%m-%d")

  start_date, end_date, date_range_str = dt.date_range(args['start-date'], args['end-date'])

  ent_file_str = input('Do you want to load entity csv files? (y/[n]: ')
  ent_file_str = ent_file_str.lower()
  if ent_file_str.find('y') < 0:
      ent_file_str = 'n'
      
  if ent_file_str.find('n') >= 0:

      # Get files needed
      ddb_info_file = filedialog.askopenfilename(initialdir = "C:\\",
                                               title = "Choose txt file with database login information...")
      with AIMS() as aims:
        entity_comm_df = get_ent_comm_phones(aims._connection)
        ent_usg_me_pref_df = get_comm_usg_preferred_phones(aims._connection)
  else:
      
      # Get entity data
      init_ent_comm_dir = 'C:\\'
      ent_comm_file = filedialog.askopenfilename(initialdir = init_ent_comm_dir,
                                               title = \
                                               "Choose the entity_comm_at data csv file...")
      
      ent_comm_usg_file = filedialog.askopenfilename(title = \
                                               "Choose the entity_comm_usg_at data csv file...")
      
      # Load entity data
      entity_comm_df = pd.read_csv(ent_comm_file, delimiter = ",", index_col = None, header = 0, dtype = str)
      entity_comm_df = entity_comm_df[entity_comm_df['comm_cat'] == 'P']
      
      entity_comm_usg_df = pd.read_csv(ent_comm_usg_file, delimiter = ",", index_col = None, header = 0, dtype = str)
      ent_usg_me_pref_df = entity_comm_usg_df[entity_comm_usg_df['comm_usage'] == 'PV']

     
  source_types = ['WEBVRTR', 'PHNSURV', 'VHCP']

  curr_datetime = datetime.datetime.now()
  curr_date_str = str(curr_datetime.year) + '-' + str(curr_datetime.month) + '-' + str(curr_datetime.day)
  curr_date = datetime.datetime.strptime(curr_date_str, '%Y-%m-%d')

  entity_comm_df = rename_comm_cols(entity_comm_df)
  ent_usg_me_pref_df = rename_usg_cols(ent_usg_me_pref_df)

  ent_no_end_ndx = entity_comm_df['ent_comm_end_dt'].isna()
  entity_comm_df.loc[ent_no_end_ndx, 'ent_comm_end_dt'] = curr_date

  entity_comm_df = set_entity_dates(entity_comm_df, 'ent_comm_begin_dt', 'ent_comm_end_dt')
  ent_usg_me_pref_df = set_entity_dates(ent_usg_me_pref_df, 'usg_begin_dt', 'usg_end_dt')

  entity_comm_df['begin_month'] = entity_comm_df['ent_comm_begin_dt'].apply(lambda x: x.month if x != None else x)
  entity_comm_df['begin_year'] = entity_comm_df['ent_comm_begin_dt'].apply(lambda x: x.year if x != None else x)
  entity_comm_df['end_month'] = entity_comm_df['ent_comm_end_dt'].apply(lambda x: x.month if x != None else x)
  entity_comm_df['end_year'] = entity_comm_df['ent_comm_end_dt'].apply(lambda x: x.year if x != None else x)

  ent_comm_usg_df = entity_comm_df.merge(ent_usg_me_pref_df, how = 'left', 
                                       left_on = ['ent_comm_entity_id', 'ent_comm_comm_id'],
                                       right_on = ['usg_entity_id', 'usg_comm_id'])
      

  # Analyze all data with begin date in range (end dated and not)
  entity_begin_df = ent_comm_usg_df[(ent_comm_usg_df['ent_comm_begin_dt'] >= start_date) & \
                                    (ent_comm_usg_df['ent_comm_begin_dt'] <= end_date)]

  ent_begin_pv_df = entity_begin_df[entity_begin_df['usg_comm_usage'].notnull()]


  month_tot_add_cnt, month_tot_pv_add_cnt = get_tot_pv_counts(entity_begin_df, ent_begin_pv_df, 
                                                              'add_month_count', 'pv_add_month_count', 
                                                              True, None)

  month_src_tot_add_cnt, month_src_tot_pv_add_cnt = get_tot_pv_counts(entity_begin_df, ent_begin_pv_df, 
                                                              'src_add_month_cnt', 'src_pv_add_month_cnt', 
                                                              True, 'ent_comm_src_cat_code')

  month_usr_tot_add_cnt, month_usr_tot_pv_add_cnt = get_tot_pv_counts(entity_begin_df, ent_begin_pv_df, 
                                                              'usr_add_month_cnt', 'usr_pv_add_month_cnt', 
                                                              True, 'ent_comm_update_user_id')

  month_update_tot_add_cnt, month_update_tot_pv_add_cnt = get_tot_pv_counts(entity_begin_df, ent_begin_pv_df, 
                                                              'usr_add_month_cnt', 'usr_pv_add_month_cnt', 
                                                              True, 'ent_comm_update_dtm')

  tot_out_file = out_dir + date_range_str + '_All_EntityLoad_Add_Analysis.xlsx'

  save_count_files(tot_out_file, month_tot_add_cnt, month_tot_pv_add_cnt, 
                        month_src_tot_add_cnt, month_src_tot_pv_add_cnt, 
                        month_usr_tot_add_cnt, month_usr_tot_pv_add_cnt, 
                        month_update_tot_add_cnt, month_update_tot_pv_add_cnt)

  # Analyze only not end dated data with begin date in range
  entity_begin_no_end_df = entity_begin_df[entity_begin_df['ent_comm_end_dt'] == curr_date]
  entity_begin_no_end_pv_df = entity_begin_no_end_df[entity_begin_no_end_df['usg_comm_usage'].notnull()]

  month_no_end_tot_add_cnt, month_no_end_tot_pv_add_cnt = get_tot_pv_counts(entity_begin_no_end_df, 
                                                                            entity_begin_no_end_pv_df, 
                                                                            'no_end_add_month_count', 
                                                                            'no_end_pv_add_month_count', 
                                                                            True, None)

  month_no_end_src_tot_add_cnt, month_no_end_src_tot_pv_add_cnt = get_tot_pv_counts(entity_begin_no_end_df, 
                                                                                    entity_begin_no_end_pv_df, 
                                                                                    'no_end_src_add_month_cnt', 
                                                                                    'no_end_src_pv_add_month_cnt', 
                                                                                    True, 'ent_comm_src_cat_code')

  month_no_end_usr_tot_add_cnt, month_no_end_usr_tot_pv_add_cnt = get_tot_pv_counts(entity_begin_no_end_df, 
                                                                                    entity_begin_no_end_pv_df, 
                                                                                    'no_end_usr_add_month_cnt', 
                                                                                    'no_end_usr_pv_add_month_cnt', 
                                                                                    True, 'ent_comm_update_user_id')

  month_no_end_update_tot_add_cnt, month_no_end_update_tot_pv_add_cnt = get_tot_pv_counts(entity_begin_no_end_df,
                                                                                          entity_begin_no_end_pv_df, 
                                                                                          'no_end_usr_add_month_cnt', 
                                                                                          'no_end_usr_pv_add_month_cnt', 
                                                                                          True, 'ent_comm_update_dtm')


  tot_no_end_out_file = out_dir + date_range_str + '_All_NoEnd_EntityLoad_Add_Analysis.xlsx'

  save_count_files(tot_no_end_out_file, month_no_end_tot_add_cnt, month_no_end_tot_pv_add_cnt, 
                        month_no_end_src_tot_add_cnt, month_no_end_src_tot_pv_add_cnt, 
                        month_no_end_usr_tot_add_cnt, month_no_end_usr_tot_pv_add_cnt, 
                        month_no_end_update_tot_add_cnt, month_no_end_update_tot_pv_add_cnt)


  entity_end_df = ent_comm_usg_df[(ent_comm_usg_df['ent_comm_end_dt'] >= start_date) & \
                                    (ent_comm_usg_df['ent_comm_end_dt'] <= end_date)]
  entity_end_df = entity_end_df[entity_end_df['ent_comm_end_dt'] != curr_date]

  ent_end_pv_df = entity_end_df[entity_end_df['usg_comm_usage'].notnull()]

      
  month_tot_del_cnt, month_tot_pv_del_cnt = get_tot_pv_counts(entity_end_df, ent_end_pv_df, 
                                                              'del_month_count', 'pv_del_month_count', 
                                                              False, None)

  month_src_tot_del_cnt, month_src_tot_pv_del_cnt = get_tot_pv_counts(entity_end_df, ent_end_pv_df, 
                                                              'src_del_month_cnt', 'src_pv_del_month_cnt', 
                                                              False, 'ent_comm_src_cat_code')

  month_usr_tot_del_cnt, month_usr_tot_pv_del_cnt = get_tot_pv_counts(entity_end_df, ent_end_pv_df, 
                                                              'usr_del_month_cnt', 'usr_pv_del_month_cnt', 
                                                              False, 'ent_comm_update_user_id')

  month_update_tot_del_cnt, month_update_tot_pv_del_cnt = get_tot_pv_counts(entity_end_df, ent_end_pv_df, 
                                                              'usr_del_month_cnt', 'usr_pv_del_month_cnt', 
                                                              False, 'ent_comm_update_dtm')

  tot_out_file = out_dir + date_range_str + '_All_EntityLoad_Delete_Analysis.xlsx'

  save_count_files(tot_out_file, month_tot_del_cnt, month_tot_pv_del_cnt, 
                        month_src_tot_del_cnt, month_src_tot_pv_del_cnt, 
                        month_usr_tot_del_cnt, month_usr_tot_pv_del_cnt, 
                        month_update_tot_del_cnt, month_update_tot_pv_del_cnt)


  for source_type in source_types:

      # Analyze all data with begin date in range (end dated and not)
      entity_source_begin_df = entity_begin_df[entity_begin_df['ent_comm_src_cat_code'] == source_type]
      ent_source_begin_pv_df = entity_source_begin_df[entity_source_begin_df['usg_comm_usage'].notnull()]


      tmp_month_tot_add_cnt, tmp_month_tot_pv_add_cnt = get_tot_pv_counts(entity_source_begin_df, 
                                                                  ent_source_begin_pv_df, 
                                                                  'add_month_count', 'pv_add_month_count', 
                                                                  True, None)
      
      tmp_month_src_tot_add_cnt, tmp_month_src_tot_pv_add_cnt = get_tot_pv_counts(entity_source_begin_df, 
                                                                  ent_source_begin_pv_df, 
                                                                  'src_add_month_cnt', 'src_pv_add_month_cnt', 
                                                                  True, 'ent_comm_src_cat_code')
      
      tmp_month_usr_tot_add_cnt, tmp_month_usr_tot_pv_add_cnt = get_tot_pv_counts(entity_source_begin_df, 
                                                                  ent_source_begin_pv_df, 
                                                                  'usr_add_month_cnt', 'usr_pv_add_month_cnt', 
                                                                  True, 'ent_comm_update_user_id')
      
      tmp_month_update_tot_add_cnt, tmp_month_update_tot_pv_add_cnt = get_tot_pv_counts(entity_source_begin_df, 
                                                                  ent_source_begin_pv_df, 
                                                                  'usr_add_month_cnt', 'usr_pv_add_month_cnt', 
                                                                  True, 'ent_comm_update_dtm')
      
      tmp_out_file = out_dir + date_range_str + '_' + source_type + '_EntityLoad_Add_Analysis.xlsx'
      
      save_count_files(tmp_out_file, tmp_month_tot_add_cnt, tmp_month_tot_pv_add_cnt, 
                            tmp_month_src_tot_add_cnt, tmp_month_src_tot_pv_add_cnt, 
                            tmp_month_usr_tot_add_cnt, tmp_month_usr_tot_pv_add_cnt, 
                            tmp_month_update_tot_add_cnt, tmp_month_update_tot_pv_add_cnt)
          
   
      # Analyze only not end dated data with begin date in range
      entity_source_no_end_df = entity_source_begin_df[entity_source_begin_df['ent_comm_end_dt'] == curr_date]
      entity_source_no_end_pv_df = entity_source_no_end_df[entity_source_no_end_df['usg_comm_usage'].notnull()]
      
      tmp_month_no_end_tot_add_cnt, tmp_month_no_end_tot_pv_add_cnt = get_tot_pv_counts(entity_source_no_end_df, 
                                                                                entity_source_no_end_pv_df, 
                                                                                'no_end_add_month_count', 
                                                                                'no_end_pv_add_month_count', 
                                                                                True, None)
      
      tmp_month_no_end_src_tot_add_cnt, tmp_month_no_end_src_tot_pv_add_cnt = get_tot_pv_counts(entity_source_no_end_df, 
                                                                                        entity_source_no_end_pv_df, 
                                                                                        'no_end_src_add_month_cnt', 
                                                                                        'no_end_src_pv_add_month_cnt', 
                                                                                        True, 'ent_comm_src_cat_code')
      
      tmp_month_no_end_usr_tot_add_cnt, tmp_month_no_end_usr_tot_pv_add_cnt = get_tot_pv_counts(entity_source_no_end_df, 
                                                                                        entity_source_no_end_pv_df, 
                                                                                        'no_end_usr_add_month_cnt', 
                                                                                        'no_end_usr_pv_add_month_cnt', 
                                                                                        True, 'ent_comm_update_user_id')
      
      tmp_month_no_end_update_tot_add_cnt, tmp_month_no_end_update_tot_pv_add_cnt = get_tot_pv_counts(entity_source_no_end_df,
                                                                                              entity_source_no_end_pv_df, 
                                                                                              'no_end_usr_add_month_cnt', 
                                                                                              'no_end_usr_pv_add_month_cnt', 
                                                                                              True, 'ent_comm_update_dtm')
      
      
      tmp_no_end_out_file = out_dir + date_range_str + '_' + source_type +  '_NoEnd_EntityLoad_Add_Analysis.xlsx'
      
      save_count_files(tot_no_end_out_file, tmp_month_no_end_tot_add_cnt, tmp_month_no_end_tot_pv_add_cnt, 
                            tmp_month_no_end_src_tot_add_cnt, tmp_month_no_end_src_tot_pv_add_cnt, 
                            tmp_month_no_end_usr_tot_add_cnt, tmp_month_no_end_usr_tot_pv_add_cnt, 
                            tmp_month_no_end_update_tot_add_cnt, tmp_month_no_end_update_tot_pv_add_cnt)
      

      entity_source_end_df = entity_end_df[entity_end_df['ent_comm_src_cat_code'] == source_type]
      ent_source_pv_end_df = entity_source_end_df[entity_source_end_df['usg_comm_usage'].notnull()]    
          
      tmp_month_tot_del_cnt, tmp_month_tot_pv_del_cnt = get_tot_pv_counts(entity_source_end_df, ent_source_pv_end_df, 
                                                                  'del_month_count', 'pv_del_month_count', 
                                                                  False, None)
      
      tmp_month_src_tot_del_cnt, tmp_month_src_tot_pv_del_cnt = get_tot_pv_counts(entity_source_end_df, 
                                                                  ent_source_pv_end_df, 
                                                                  'src_del_month_cnt', 'src_pv_del_month_cnt', 
                                                                  False, 'ent_comm_src_cat_code')
      
      tmp_month_usr_tot_del_cnt, tmp_month_usr_tot_pv_del_cnt = get_tot_pv_counts(entity_source_end_df, 
                                                                  ent_source_pv_end_df, 
                                                                  'usr_del_month_cnt', 'usr_pv_del_month_cnt', 
                                                                  False, 'ent_comm_update_user_id')
      
      tmp_month_update_tot_del_cnt, tmp_month_update_tot_pv_del_cnt = get_tot_pv_counts(entity_source_end_df, 
                                                                  ent_source_pv_end_df, 
                                                                  'usr_del_month_cnt', 'usr_pv_del_month_cnt', 
                                                                  False, 'ent_comm_update_dtm')
      
      tot_out_file = out_dir + date_range_str + '_' + source_type +  '_EntityLoad_Delete_Analysis.xlsx'
      
      save_count_files(tot_out_file, tmp_month_tot_del_cnt, tmp_month_tot_pv_del_cnt, 
                            tmp_month_src_tot_del_cnt, tmp_month_src_tot_pv_del_cnt, 
                            tmp_month_usr_tot_del_cnt, tmp_month_usr_tot_pv_del_cnt, 
                            tmp_month_update_tot_del_cnt, tmp_month_update_tot_pv_del_cnt)


def get_count_by_mon_yr(entity_df, count_var_name, group_vars):
    
    month_cnt = entity_df.sort_values(group_vars).groupby(group_vars).size().reset_index()
    month_cnt = month_cnt.rename(columns = {0:count_var_name})
    
    return month_cnt
    
    
def get_tot_pv_counts(entity_df, ent_pv_df, count_var_name, pv_count_var_name, begin_flag = True, 
                      additional_var = None):
    
    if begin_flag == True:
        group_vars = ['begin_year', 'begin_month']
    else:
        group_vars = ['end_year', 'end_month']
        
    if additional_var != None:
        group_vars.append(additional_var)        
    
    month_tot_add_cnt = get_count_by_mon_yr(entity_df, count_var_name, group_vars)
    month_tot_pv_add_cnt = get_count_by_mon_yr(ent_pv_df, pv_count_var_name, group_vars)
           
    return month_tot_add_cnt, month_tot_pv_add_cnt
    
   
def save_count_files(out_file, month_tot_add_cnt, month_tot_pv_add_cnt, 
                      month_src_tot_add_cnt, month_src_tot_pv_add_cnt, 
                      month_usr_tot_add_cnt, month_usr_tot_pv_add_cnt, 
                      month_update_tot_add_cnt, month_update_tot_pv_add_cnt):
    
    res_writer = pd.ExcelWriter(out_file, engine = 'xlsxwriter')

    month_count_sheet = 'month_tot_count'
    month_tot_add_cnt.to_excel(res_writer, sheet_name = month_count_sheet, index = False, header = True)  
        
    pv_month_count_sheet = 'pv_month_count'
    month_tot_pv_add_cnt.to_excel(res_writer, sheet_name = pv_month_count_sheet, index = False, header = True)  
        
    month_count_sheet = 'src_month_tot_count'
    month_src_tot_add_cnt.to_excel(res_writer, sheet_name = month_count_sheet, index = False, header = True)  
        
    pv_month_count_sheet = 'src_pv_month_count'
    month_src_tot_pv_add_cnt.to_excel(res_writer, sheet_name = pv_month_count_sheet, index = False, header = True)  
        
    month_count_sheet = 'usr_month_tot_count'
    month_usr_tot_add_cnt.to_excel(res_writer, sheet_name = month_count_sheet, index = False, header = True)  
        
    pv_month_count_sheet = 'usr_pv_month_count'
    month_usr_tot_pv_add_cnt.to_excel(res_writer, sheet_name = pv_month_count_sheet, index = False, header = True)  
        
    month_count_sheet = 'update_month_tot_count'
    month_update_tot_add_cnt.to_excel(res_writer, sheet_name = month_count_sheet, index = False, header = True)  
        
    pv_month_count_sheet = 'update_pv_month_count'
    month_update_tot_pv_add_cnt.to_excel(res_writer, sheet_name = pv_month_count_sheet, index = False, header = True)  
        
    res_writer.save()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-s', '--start-date', required=True,
                    help='WSLive data start date in the form YYYY-MM[-DD] (default day is 1).')
    ap.add_argument('-e', '--end-date', required=True,
                    help='WSLive data end date in the form YYYY-MM[-DD] (default day is last day of month).')
    args = vars(ap.parse_args())

    main(args)
