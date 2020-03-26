# Kari Palmier    Created 8/26/19
#
#############################################################################
import pandas as pd
import tkinter as tk
from tkinter import filedialog


# Get path of general (common) code and add it to the python path variable
import sys
import os
curr_path = os.path.abspath(__file__)
slash_ndx = [i for i in range(len(curr_path)) if curr_path.startswith('\\', i)]
base_path = curr_path[:slash_ndx[-2]+1]
gen_path = base_path + 'Common_Code\\'
sys.path.insert(0, gen_path)

from get_input_date_range import get_input_date_range
import datalabs.curate.dataframe as df

gen_path = base_path + 'Common_Model_Code\\'
sys.path.insert(0, gen_path)

from analyze_scored_survey_results import analyze_survey_class_results, analyze_survey_binned_results
from create_addr_model_input_data import create_addr_key

import warnings
warnings.filterwarnings("ignore")

    
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
    
init_pred_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Polo_Rank_Model\\Analysis\\'
wslive_pred_sample_file = filedialog.askopenfilename(initialdir = init_pred_dir,
                                         title = "Choose wslive file with predictions...")

init_anlys_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Polo_Rank_Model\\Analysis\\'
anlys_out_dir = filedialog.askdirectory(initialdir = init_anlys_dir,
                                         title = "Choose directory to save analysis output...")
anlys_out_dir = anlys_out_dir.replace("/", "\\")
anlys_out_dir += "\\"

start_date, end_date, date_range_str = get_input_date_range()

old_stdout = sys.stdout
log_filename = anlys_out_dir + date_range_str + '_WSLive_PoloRank_Scoring_Analysis_Log.txt'
log_file = open(log_filename, "w")
sys.stdout = log_file

source_code = ['C', 'Z']

# Read in wslive data
if data_type == '2':
    wslive_results_df = pd.read_csv(wslive_results_file, delimiter = ",", index_col = None, header = 0, dtype = str)
    wslive_results_df = df.rename_in_upper_case(wslive_results_df)
    
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
    
wslive_pred_sample_df = df.rename_in_upper_case(wslive_pred_sample_df)


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
    
    wslive_pred_df = create_addr_key(wslive_pred_df, 'INIT_POLO_MAILING_LINE_2', 'INIT_POLO_ZIP',
                                    'INIT_SMPL_ST_NUM', 'INIT_SMPL_ADDR_KEY')
    
    wslive_pred_df = create_addr_key(wslive_pred_df, 'OFFICE_ADDRESS_LINE_2', 'OFFICE_ADDRESS_ZIP',
                                    'WSLIVE_ST_NUM', 'WSLIVE_ADDR_KEY')
    
    wslive_pred_df['ACTUAL_CLASS'] = 0
    target_one_ndx = (wslive_pred_df['ent_addr_key'] == wslive_pred_df['WSLIVE_ADDR_KEY']) & \
        ((wslive_pred_df['ADDR_STATUS'] == 'Confirmed') | ((wslive_pred_df['ADDR_STATUS'] == 'Updated') & \
        (wslive_pred_df['INIT_SMPL_ADDR_KEY'] == wslive_pred_df['WSLIVE_ADDR_KEY'])))
    wslive_pred_df.loc[target_one_ndx, 'ACTUAL_CLASS'] = 1
    

wslive_pred_df['ACTUAL_CLASS'] = wslive_pred_df['ACTUAL_CLASS'].astype('int')
wslive_pred_df['PRED_CLASS'] = wslive_pred_df['PRED_CLASS'].astype('float').astype('int')
wslive_pred_df['PRED_PROBABILITY'] = wslive_pred_df['PRED_PROBABILITY'].astype('float')


print('-----------------------------------------------------')
print('Results Including Inconclusive and No Contact Results')
print('-----------------------------------------------------')
print('\n')

conf_mat_all, class_mat_all, score_df_all = analyze_survey_class_results(wslive_pred_df)

save_file = anlys_out_dir + date_range_str + '_WSLive_PoloRank_Class_Results_All.xlsx'
writer = pd.ExcelWriter(save_file, engine = 'xlsxwriter')
score_df_all.to_excel(writer, sheet_name = 'class_scores', index = True, header = True)
class_mat_all.to_excel(writer, sheet_name = 'class_matrix', index = True, header = True)
writer.save()


print('-----------------------------------------------------')
print('Results Excluding Inconclusive and No Contact Results')
print('-----------------------------------------------------')
print('\n')

wslive_filter_df = wslive_pred_df[wslive_pred_df['ADDR_STATUS'].isin(['CONFIRMED', 'UPDATED'])]

conf_mat_filter, class_mat_filter, score_df_filter = analyze_survey_class_results(wslive_filter_df)

save_file = anlys_out_dir + date_range_str + '_WSLive_PoloRank_Class_Results_Filtered.xlsx'
writer = pd.ExcelWriter(save_file, engine = 'xlsxwriter')
score_df_filter.to_excel(writer, sheet_name = 'class_scores', index = True, header = True)
class_mat_filter.to_excel(writer, sheet_name = 'class_matrix', index = True, header = True)
writer.save()

bin_step = 0.05
bin_df_0p05 = analyze_survey_binned_results(wslive_pred_df, bin_step, 'ADDR_STATUS')

num_rows = bin_df_0p05.shape[0] + 1
num_cols = bin_df_0p05.shape[1] + 1
pd.set_option('max_rows', num_rows)
pd.set_option('max_columns', num_cols)
    
print('Bin Confirmed/Updated/Known Bad/etc Results - Bin Size 0.05')
print('-----------------------------------------------------------')
print(bin_df_0p05)
print('\n')
    

bin_save_file = anlys_out_dir + date_range_str + '_WSLive_PoloRank_Bin_Analysis.xlsx'
writer = pd.ExcelWriter(bin_save_file, engine = 'xlsxwriter')
bin_df_0p05.to_excel(writer, sheet_name = 'step_size_0.05', index = None, header = True)

bin_step = 0.1
bin_df_0p1 = analyze_survey_binned_results(wslive_pred_df, bin_step, 'ADDR_STATUS')

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
 
