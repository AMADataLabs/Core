# Kari Palmier    Created 8/8/19
# Kari Palmier    Updated to filter known bad by if they are in current PPD
#
#############################################################################
import argparse
import os
import sys
import datetime
import tkinter as tk
from tkinter import filedialog

import pandas as pd

import settings
from select_files import select_files
from combine_data import combine_data
import datalabs.curate.dataframe as df
import datalabs.util.datetime as dt


def main(args):
  root = tk.Tk()
  root.withdraw()

  init_wslive_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\WSLive\\'
  wslive_results_file = filedialog.askopenfilename(initialdir = init_wslive_dir,
                                           title = "Choose WSLive file with results encoded...")

  print('\n\n')
  smpl_str = input('Do you want to match results to samples sent? (y/[n]): ')
  smpl_str = smpl_str.lower()
  if smpl_str.find('y') < 0:
      smpl_str = 'n'
      
  sample_paths = []
  if smpl_str == 'y':
      init_sample_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Survey_Samples\\'
      sample_paths = select_files(init_sample_dir, 'Select file(s) from standard survey')

      
  start_date, end_date, date_range_str = dt.date_range(args['start-date'], args['end-date'])

  current_time = datetime.datetime.now()
  start_time_str = current_time.strftime("%Y-%m-%d")

  # Read in samples sent
  if len(sample_paths) > 0:
      sample_df = combine_data(sample_paths, None, 0)
      sample_df = df.rename_in_upper_case(sample_df)

  # Read in wslive data
  wslive_results_df = pd.read_csv(wslive_results_file, delimiter = ",", index_col = None, header = 0, dtype = str)
  wslive_results_df = df.rename_in_upper_case(wslive_results_df)

  # Get data for date range specified
  wslive_results_df['WSLIVE_FILE_DT'] = pd.to_datetime(wslive_results_df['WSLIVE_FILE_DT'])
  wslive_res_date_df = wslive_results_df[(wslive_results_df['WSLIVE_FILE_DT'] >= start_date) & \
                                    (wslive_results_df['WSLIVE_FILE_DT'] <= end_date)]
              
  # Join results with sample sent on ME
  if len(sample_paths) > 0:
      wslive_res_smpl_df = wslive_res_date_df.merge(sample_df, how = 'inner', 
                                                    left_on = ['PHYSICIAN_ME_NUMBER',
                                                               'OFFICE_TELEPHONE'],
                                                   right_on = ['ME', 'TELEPHONE_NUMBER'])
  else:
      wslive_res_smpl_df = wslive_results_df

  print('\n')
  print('Standard Survey Result Counts')
  print('-----------------------------')

  # Loop over source types and compile results for each
  survey_sources = [['C', 'Z'], 'CR', 'CA', 'CB', 'Q', 'S', 'VT']
  survey_names = ['MF', 'MF Random', 'MF Risky W Email', 'MF Risky No Email', 
                  'IQVIA', 'Symphony', 'Vertical Trail']

  for i in range(len(survey_sources)):
      
      source_code = survey_sources[i]
      survey_name = survey_names[i]
          
      # If source type for MF is a list so need to treat differently
      if type(source_code).__name__ == 'list':
          source_ndx = wslive_res_smpl_df['SOURCE'].isin(source_code)
      else:
          source_ndx = wslive_res_smpl_df['SOURCE'] == source_code
          
      print('{} Count: {}'.format(survey_name, sum(source_ndx)))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-s', '--start-date', required=True,
                    help='WSLive data start date in the form YYYY-MM[-DD] (default day is 1).')
    ap.add_argument('-e', '--end-date', required=True,
                    help='WSLive data end date in the form YYYY-MM[-DD] (default day is last day of month).')
    args = vars(ap.parse_args())

    main(args)
