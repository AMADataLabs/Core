# Kari Palmier    7/31/19    Created
# Kari Palmier    8/14/19    Updated to work with more generic get_sample
#
#############################################################################
import argparse
import datetime
import os
import pickle 
import sys
import tkinter as tk
import warnings

import pandas as pd

import settings

# Sandbox/CommonModelCode/
from score_phone_ppd_data import score_phone_wslive_data
from class_model_creation import get_prob_info, get_pred_info
from create_phone_model_input_data import create_model_initial_data
from get_entity_ppd_info import clean_ent_comm_data, clean_phn_data, clean_ent_usg_data
from get_entity_ppd_info import clean_fone_zr_data, create_ent_me_data

from   datalabs.access.wslive import WSLiveFile
import datalabs.curate.wslive as wslive
import datalabs.curate.dataframe  # pylint: disable=unused-import
import datalabs.util.datetime as dt


def main(args):
    root = tk.Tk()
    root.withdraw()

    init_wslive_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\WSLive\\'
    wslive_results_file = tk.filedialog.askopenfilename(initialdir = init_wslive_dir,
                                             title = "Choose wslive file with results encoded...")

    init_ppd_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\PPD\\'
    ppd_file_lst = tk.filedialog.askopenfilenames(initialdir = init_ppd_dir,
                                            title = \
                                            "Choose the PPD files used to generate the WSLive samples...")

    # Get model file needed
    model_file = tk.filedialog.askopenfilename(initialdir = "U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Phone_Disconnect_Model\\",
                                             title = "Choose the phone disconnect model sav file...")

    # Get model file needed
    model_var_file = tk.filedialog.askopenfilename(title = "Choose the phone disconnect model feature list sav file...")

    init_save_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Phone_Disconnect_Model\\Analysis\\'
    ppd_score_out_dir = tk.filedialog.askdirectory(initialdir = init_save_dir,
                                             title = "Choose directory to save the scored WSLive data in...")

    ppd_score_out_dir = ppd_score_out_dir.replace("/", "\\")
    ppd_score_out_dir += "\\"
         
    support_dir = ppd_score_out_dir + 'Support\\'  
    if not os.path.exists(support_dir):
        os.mkdir(support_dir)
      

    start_date, end_date, date_range_str = dt.date_range(args['start-date'], args['end-date'])

    init_sample_dir = \
        'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\WSLive\\Model_Init_Samples\\'
    init_sample_file_lst = tk.filedialog.askopenfilenames(initialdir = init_sample_dir,
                           title = \
                           "Choose the WSLive standard samples sent to Humach for dates chosen...")

    init_ent_comm_dir = 'C:\\'
    ent_comm_file = tk.filedialog.askopenfilename(initialdir = init_ent_comm_dir,
                                             title = \
                                             "Choose the entity_comm_at data csv file...")

    ent_comm_usg_file = tk.filedialog.askopenfilename(title = \
                                             "Choose the entity_comm_usg_at data csv file...")

    phone_file = tk.filedialog.askopenfilename(title = \
                                                "Choose the phone_at data csv file...")

    license_file = tk.filedialog.askopenfilename(title = \
                                                "Choose the license_lt data csv file...")

    ent_key_file = tk.filedialog.askopenfilename(title = \
                                                "Choose the entity_key_et data csv file...")

    fone_zr_file = tk.filedialog.askopenfilename(title = \
                                                "Choose the fone_zr data csv file...")

    current_time = datetime.datetime.now()
    start_time_str = current_time.strftime("%Y-%m-%d")

    # Get latest model and variables
    model_vars = pickle.load(open(model_var_file, 'rb'))
    model = pickle.load(open(model_file, 'rb'))

    # Load entity data
    ent_comm_df = pd.read_csv(ent_comm_file, delimiter = ",", index_col = None, header = 0, dtype = str)
    ent_comm_df = ent_comm_df[ent_comm_df['comm_cat'] == 'P']

    ent_comm_usg_df = pd.read_csv(ent_comm_usg_file, delimiter = ",", index_col = None, header = 0, dtype = str)
    ent_comm_usg_df = ent_comm_usg_df[ent_comm_usg_df['comm_cat'] == 'P']

    phone_df = pd.read_csv(phone_file, delimiter = ",", index_col = None, header = 0, dtype = str)

    license_df = pd.read_csv(license_file, delimiter = ",", index_col = None, header = 0, dtype = str)

    ent_key_df = pd.read_csv(ent_key_file, delimiter = ",", index_col = None, header = 0, dtype = str)

    fone_zr_df = pd.read_csv(fone_zr_file, delimiter = ",", index_col = None, header = 0, dtype = str)


    ent_comm_df = clean_ent_comm_data(ent_comm_df)    
    phone_df = clean_phn_data(phone_df)
    ent_comm_usg_df = clean_ent_usg_data(ent_comm_usg_df)
    ent_key_df = create_ent_me_data(ent_key_df)
    fone_zr_df = clean_fone_zr_data(fone_zr_df)


    wslive_results_df = WSLiveFile.load(wslive_results_file)

    # Get data for date range specified
    wslive_date_df = wslive_results_df[(wslive_results_df['WSLIVE_FILE_DT'] >= start_date) & \
                                      (wslive_results_df['WSLIVE_FILE_DT'] <= end_date)]

    ppd_scoring_df = create_model_initial_data(wslive_uniq_me_df, init_sample_file_lst, 
                                             ppd_file_lst, ent_comm_df, ent_comm_usg_df, 
                                             phone_df, license_df, ent_key_df, fone_zr_df)

    ppd_entity_file = support_dir + date_range_str + '_Phone_Disconnect_WSLive_Entity_Data.csv'
    ppd_scoring_df.to_csv(ppd_entity_file, sep = ',', header = True, index = True)
            
        
    wslive_pred_df, model_data_pruned = score_phone_wslive_data(ppd_scoring_df, model, model_vars)
    wslive_pred_df = wslive_pred_df.datalabs.rename_in_upper_case()

    print('\n')
    print('Prediction Information')
    print('----------------------')
    get_prob_info(wslive_pred_df['PRED_PROBABILITY'])
    get_pred_info(wslive_pred_df['PRED_CLASS'])

    wslive_pred_df['ACTUAL_CLASS'] = 0
    target_one_ndx = (wslive_pred_df['COMMENTS'] == 'Not In Service') | \
        (wslive_pred_df['COMMENTS'] == 'NOT IN SERVICE')
    wslive_pred_df.loc[target_one_ndx, 'ACTUAL_CLASS'] = 1

    print('\n')
    print('Actual Information')
    print('------------------')
    get_pred_info(wslive_pred_df['ACTUAL_CLASS'])

    ppd_dpc_output_file = ppd_score_out_dir + date_range_str + '_Phone_Disconnect_Scored_WSLive.csv'
    wslive_pred_df.to_csv(ppd_dpc_output_file, sep = ',', header = True, index = True)

    model_input_file = support_dir + start_time_str + '_PPD_' + date_range_str + '_Phone_Disconnect_WSLive_Input_Data.csv'
    model_data_pruned.to_csv(model_input_file, sep = ',', header = True, index = True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-s', '--start-date', required=True,
                    help='WSLive data start date in the form YYYY-MM[-DD] (default day is 1).')
    ap.add_argument('-e', '--end-date', required=True,
                    help='WSLive data end date in the form YYYY-MM[-DD] (default day is last day of month).')
    args = vars(ap.parse_args())

    main(args)

