# Kari Palmier    Created 8/26/19
#
#############################################################################
import argparse
import os
import sys
import tkinter as tk
from tkinter import filedialog

import pandas as pd

import settings
from analyze_scored_survey_results import analyze_survey_class_results, analyze_survey_binned_results

import datalabs.curate.dataframe  # pylint: disable=unused-import
import datalabs.util.datetime as dt


def main(args):
  root = tk.Tk()
  root.withdraw()

  print('1 - Use WSLive Result file with Predictions in it')
  print('2 - Use Separate WSLive Result and Prediction files')
  data_type = input('Enter the type of WSLive data desired ([1]): ')
  if data_type.find('2') < 0:
      data_type = '1'


  if data_type == '2':
      init_wslive_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\WSLive\\'
      wslive_results_file = filedialog.askopenfilename(initialdir = init_wslive_dir,
                                               title = "Choose wslive file with results encoded...")   
      
  init_pred_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Phone_Disconnect_Model\\Analysis\\'
  wslive_pred_sample_file = filedialog.askopenfilename(initialdir = init_pred_dir,
                                           title = "Choose wslive file with predictions...")

  init_anlys_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Phone_Disconnect_Model\\Analysis\\'
  anlys_out_dir = filedialog.askdirectory(initialdir = init_anlys_dir,
                                           title = "Choose directory to save analysis output...")
  anlys_out_dir = anlys_out_dir.replace("/", "\\")
  anlys_out_dir += "\\"

  start_date, end_date, date_range_str = dt.date_range(args['start-date'], args['end-date'])

  old_stdout = sys.stdout
  log_filename = anlys_out_dir + date_range_str + '_WSLive_PhoneDisconnect_Scoring_Analysis_Log.txt'
  log_file = open(log_filename, "w")
  sys.stdout = log_file

  source_code = ['C', 'Z']

  # Read in wslive data
  if data_type == '2':
      wslive_results_df = pd.read_csv(wslive_results_file, delimiter = ",", index_col = None, header = 0, dtype = str)
      wslive_results_df = wslive_results_df.datalabs.rename_in_upper_case()
      
      # Get data for date range specified
      wslive_results_df['WSLIVE_FILE_DT'] = pd.to_datetime(wslive_results_df['WSLIVE_FILE_DT'])
      wslive_date_df = wslive_results_df[(wslive_results_df['WSLIVE_FILE_DT'] >= start_date) & \
                                        (wslive_results_df['WSLIVE_FILE_DT'] <= end_date)]
              
      # If source type for MF is a list so need to treat differently
      wslive_source_df = wslive_date_df[wslive_date_df['SOURCE'].isin(source_code)]

      
  if wslive_pred_sample_file.find('.csv') >= 0:
      wslive_pred_sample_df = pd.read_csv(wslive_pred_sample_file, delimiter = ",", index_col = None, header = 0, dtype = str)
  else:
      wslive_pred_sample_df = pd.read_excel(wslive_pred_sample_file, index_col = None, header = 0, dtype = str)
      
  wslive_pred_sample_df = wslive_pred_sample_df.datalabs.rename_in_upper_case()


  if data_type == '2':
      wslive_preds_only_df = wslive_pred_sample_df[['ME', 'PRED_CLASS', 'PRED_PROBABILITY', 'ROUND_RANK', 
                                                    'POLO_MAILING_LINE_2', 'POLO_ZIP']]
      wslive_preds_only_df = wslive_preds_only_df.rename(columns = {'POLO_MAILING_LINE_2':'INIT_POLO_MAILING_LINE_2',
                                                                    'POLO_ZIP':'INIT_POLO_ZIP'})
      wslive_pred_df = wslive_source_df.merge(wslive_preds_only_df, how = 'inner', 
                                            left_on = ['PHYSICIAN_ME_NUMBER'],
                                            right_on = ['ME'])
  else:
      # Get data for date range specified
      wslive_pred_sample_df['WSLIVE_FILE_DT'] = pd.to_datetime(wslive_pred_sample_df['WSLIVE_FILE_DT'])
      wslive_date_df = wslive_pred_sample_df[(wslive_pred_sample_df['WSLIVE_FILE_DT'] >= start_date) & \
                                        (wslive_pred_sample_df['WSLIVE_FILE_DT'] <= end_date)]
          
      # If source type for MF is a list so need to treat differently
      wslive_pred_df = wslive_date_df[wslive_date_df['SOURCE'].isin(source_code)]


  if 'ACTUAL_CLASS' not in list(wslive_pred_df.columns.values):
      
      wslive_pred_df['ACTUAL_CLASS'] = 0
      target_one_ndx = (wslive_pred_df['COMMENTS'] == 'Not In Service') | \
          (wslive_pred_df['COMMENTS'] == 'NOT IN SERVICE')
      wslive_pred_df.loc[target_one_ndx, 'ACTUAL_CLASS'] = 1
      

  wslive_pred_df['ACTUAL_CLASS'] = wslive_pred_df['ACTUAL_CLASS'].astype('int')
  wslive_pred_df['PRED_CLASS'] = wslive_pred_df['PRED_CLASS'].astype('float').astype('int')
  wslive_pred_df['PRED_PROBABILITY'] = wslive_pred_df['PRED_PROBABILITY'].astype('float')


  print('-----------------------------------------------------')
  print('Results Including Inconclusive and No Contact Results')
  print('-----------------------------------------------------')
  print('\n')

  conf_mat_all, class_mat_all, score_df_all = analyze_survey_class_results(wslive_pred_df)

  save_file = anlys_out_dir + date_range_str + '_WSLive_PhoneDisconnect_Class_Results_All.xlsx'
  writer = pd.ExcelWriter(save_file, engine = 'xlsxwriter')
  score_df_all.to_excel(writer, sheet_name = 'class_scores', index = True, header = True)
  class_mat_all.to_excel(writer, sheet_name = 'class_matrix', index = True, header = True)
  writer.save()


  print('-----------------------------------------------------')
  print('Results Excluding Inconclusive and No Contact Results')
  print('-----------------------------------------------------')
  print('\n')

  wslive_filter_df = wslive_pred_df[wslive_pred_df['PHONE_STATUS'].isin(['CONFIRMED', 'UPDATED', 
                                    'KNOWN BAD', 'INCONCLUSIVE'])]

  conf_mat_filter, class_mat_filter, score_df_filter = analyze_survey_class_results(wslive_filter_df)

  save_file = anlys_out_dir + date_range_str + '_WSLive_PhoneDisconnect_Class_Results_Filtered.xlsx'
  writer = pd.ExcelWriter(save_file, engine = 'xlsxwriter')
  score_df_filter.to_excel(writer, sheet_name = 'class_scores', index = True, header = True)
  class_mat_filter.to_excel(writer, sheet_name = 'class_matrix', index = True, header = True)
  writer.save()

  bin_step = 0.05
  bin_df_0p05 = analyze_survey_binned_results(wslive_pred_df, bin_step, 'PHONE_STATUS')

  num_rows = bin_df_0p05.shape[0] + 1
  num_cols = bin_df_0p05.shape[1] + 1
  pd.set_option('max_rows', num_rows)
  pd.set_option('max_columns', num_cols)
      
  print('Bin Confirmed/Updated/Known Bad/etc Results - Bin Size 0.05')
  print('-----------------------------------------------------------')
  print(bin_df_0p05)
  print('\n')
      

  bin_save_file = anlys_out_dir + date_range_str + '_WSLive_PhoneDisconnect_Bin_Analysis.xlsx'
  writer = pd.ExcelWriter(bin_save_file, engine = 'xlsxwriter')
  bin_df_0p05.to_excel(writer, sheet_name = 'step_size_0.05', index = None, header = True)

  bin_step = 0.1
  bin_df_0p1 = analyze_survey_binned_results(wslive_pred_df, bin_step, 'PHONE_STATUS')

  num_rows = bin_df_0p1.shape[0] + 1
  num_cols = bin_df_0p1.shape[1] + 1
  pd.set_option('max_rows', num_rows)
  pd.set_option('max_columns', num_cols)
      
  print('Bin Confirmed/Updated/Known Bad/etc Results - Bin Size 0.1')
  print('----------------------------------------------------------')
  print(bin_df_0p1)
  print('\n')
      

  bin_df_0p1.to_excel(writer, sheet_name = 'step_size_0.1', index = None, header = True)
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

