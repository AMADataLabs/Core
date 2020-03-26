# Kari Palmier    7/31/19    Created
# Kari Palmier    8/14/19    Updated to work with more generic get_sample
#
#############################################################################
import datetime
import os
import pickle 
import sys
import tkinter as tk
import warnings

import pandas as pd

import settings
import datalabs.curate.wslive as wslive

# Sandbox/CommonCode/
from capitalize_column_names import capitalize_column_names
from get_input_date_range import get_input_date_range

# Sandbox/CommonModelCode/
from score_phone_ppd_data import score_phone_wslive_data
from class_model_creation import get_prob_info, get_pred_info
from create_phone_model_input_data import create_model_initial_data
from get_entity_ppd_info import clean_ent_comm_data, clean_phn_data, clean_ent_usg_data
from get_entity_ppd_info import clean_fone_zr_data, create_ent_me_data


warnings.filterwarnings("ignore")

    
root = tk.Tk()
root.withdraw()

init_wslive_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\WSLive\\'
wslive_results_file = tk.filedialog.askopenfilename(initialdir=init_wslive_dir,
                                                 title="Choose wslive file with results encoded...")

init_ppd_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\PPD\\'
ppd_file_lst = tk.filedialog.askopenfilenames(initialdir=init_ppd_dir,
                                           title="Choose the PPD files used to generate the WSLive samples...")

# Get model file needed
model_file = tk.filedialog.askopenfilename(initialdir="U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Phone_Quality_Model\\",
                                        title="Choose the phone quality model sav file...")

# Get model file needed
model_var_file = tk.filedialog.askopenfilename(title="Choose the phone quality model feature list sav file...")

init_save_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Phone_Quality_Model\\Analysis\\'
ppd_score_out_dir = tk.filedialog.askdirectory(initialdir=init_save_dir,
                                            title="Choose directory to save the scored WSLive data in...")

ppd_score_out_dir = ppd_score_out_dir.replace("/", "\\")
ppd_score_out_dir += "\\"
     
support_dir = ppd_score_out_dir + 'Support\\'  
if not os.path.exists(support_dir):
    os.mkdir(support_dir)
  

start_date, end_date, date_range_str = get_input_date_range()

init_sample_dir = \
    'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\WSLive\\Model_Init_Samples\\'
init_sample_file_lst = tk.filedialog.askopenfilenames(initialdir=init_sample_dir,
                                                   title="Choose the WSLive standard samples sent to Humach for dates chosen...")

init_ent_comm_dir = 'C:\\'
ent_comm_file = tk.filedialog.askopenfilename(initialdir=init_ent_comm_dir,
                                           title="Choose the entity_comm_at data csv file...")

ent_comm_usg_file = tk.filedialog.askopenfilename(title="Choose the entity_comm_usg_at data csv file...")

phone_file = tk.filedialog.askopenfilename(title="Choose the phone_at data csv file...")

license_file = tk.filedialog.askopenfilename(title="Choose the license_lt data csv file...")

ent_key_file = tk.filedialog.askopenfilename(title="Choose the entity_key_et data csv file...")

fone_zr_file = tk.filedialog.askopenfilename(title="Choose the fone_zr data csv file...")

current_time = datetime.datetime.now()
start_time_str = current_time.strftime("%Y-%m-%d")

# Get latest model and variables
model_vars = pickle.load(open(model_var_file, 'rb'))
model = pickle.load(open(model_file, 'rb'))

# Load entity data
ent_comm_df = pd.read_csv(ent_comm_file, delimiter=",", index_col=None, header=0, dtype=str)
ent_comm_df = ent_comm_df[ent_comm_df['comm_cat'] == 'P']

ent_comm_usg_df = pd.read_csv(ent_comm_usg_file, delimiter=",", index_col=None, header=0, dtype=str)
ent_comm_usg_df = ent_comm_usg_df[ent_comm_usg_df['comm_cat'] == 'P']

phone_df = pd.read_csv(phone_file, delimiter=",", index_col=None, header=0, dtype=str)

license_df = pd.read_csv(license_file, delimiter=",", index_col=None, header=0, dtype=str)

ent_key_df = pd.read_csv(ent_key_file, delimiter=",", index_col=None, header=0, dtype=str)

fone_zr_df = pd.read_csv(fone_zr_file, delimiter=",", index_col=None, header=0, dtype=str)


ent_comm_df = clean_ent_comm_data(ent_comm_df)    
phone_df = clean_phn_data(phone_df)
ent_comm_usg_df = clean_ent_usg_data(ent_comm_usg_df)
ent_key_df = create_ent_me_data(ent_key_df)
fone_zr_df = clean_fone_zr_data(fone_zr_df)


# Read in wslive data
wslive_results_df = pd.read_csv(wslive_results_file, delimiter=",", index_col=None,
                                header=0, dtype=str)
wslive_results_df = capitalize_column_names(wslive_results_df)

# Get data for date range specified
wslive_results_df['WSLIVE_FILE_DT'] = pd.to_datetime(wslive_results_df['WSLIVE_FILE_DT'])
wslive_date_df = wslive_results_df[(wslive_results_df['WSLIVE_FILE_DT'] >= start_date) &
                                   (wslive_results_df['WSLIVE_FILE_DT'] <= end_date)]

# TODO: This should be part of the cleaning stage so we have standardized input data
wslive_date_df = wslive.standardize(wslive_date_df)

wslive_uniq_me_df = wslive.most_recent_by_me_number(wslive_date_df)

ppd_scoring_df = create_model_initial_data(wslive_uniq_me_df, init_sample_file_lst, 
                                           ppd_file_lst, ent_comm_df, ent_comm_usg_df,
                                           phone_df, license_df, ent_key_df, fone_zr_df)

ppd_entity_file = support_dir + date_range_str + '_Phone_Quality_WSLive_Entity_Data.csv'
ppd_scoring_df.to_csv(ppd_entity_file, sep=',', header=True, index=True)
        
    
wslive_pred_df, model_data_pruned = score_phone_wslive_data(ppd_scoring_df, model, model_vars)
wslive_pred_df = capitalize_column_names(wslive_pred_df)

print('\n')
print('Prediction Information')
print('----------------------')
get_prob_info(wslive_pred_df['PRED_PROBABILITY'])
get_pred_info(wslive_pred_df['PRED_CLASS'])

wslive_pred_df['ACTUAL_CLASS'] = 0
target_one_ndx = (wslive_pred_df['PHONE_STATUS'] == 'CONFIRMED') | ((wslive_pred_df['PHONE_STATUS'] == 'UPDATED') & \
    (wslive_pred_df['INIT_TELEPHONE_NUMBER'] == wslive_pred_df['OFFICE_TELEPHONE']))
wslive_pred_df.loc[target_one_ndx, 'ACTUAL_CLASS'] = 1

print('\n')
print('Actual Information')
print('------------------')
get_pred_info(wslive_pred_df['ACTUAL_CLASS'])

ppd_dpc_output_file = ppd_score_out_dir + date_range_str + '_Phone_Quality_Scored_WSLive.csv'
wslive_pred_df.to_csv(ppd_dpc_output_file, sep=',', header=True, index=True)

model_input_file = support_dir + start_time_str + '_PPD_' + date_range_str + '_Phone_Quality_WSLive_Input_Data.csv'
model_data_pruned.to_csv(model_input_file, sep=',', header=True, index=True)
