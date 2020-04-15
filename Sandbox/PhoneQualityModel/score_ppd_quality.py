1# Kari Palmier    7/31/19    Created
# Kari Palmier    8/14/19    Updated to work with more generic get_sample
#
#############################################################################
import datetime
import os
import pickle 
import sys
import tkinter as tk
from tkinter import filedialog

import pandas as pd

from get_ppd import get_latest_ppd_data

from score_phone_ppd_data import score_phone_ppd_data
from class_model_creation import get_prob_info, get_pred_info
from create_phone_model_input_data import create_ppd_scoring_data
from get_entity_ppd_info import clean_ent_comm_data, clean_phn_data, clean_ent_usg_data
from get_entity_ppd_info import clean_fone_zr_data, create_ent_me_data

import datalabs.curate.dataframe  # pylint: disable=unused-import

    
root = tk.Tk()
root.withdraw()

# Get model file needed
model_file = filedialog.askopenfilename(initialdir="U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Phone_Quality_Model\\",
                                        title="Choose the current phone quality model sav file...")

# Get model file needed
model_var_file = filedialog.askopenfilename(title="Choose the current phone quality model feature list sav file...")

print('1 - Choose PPD csv file')
print('2 - Use latest PPD')
ppd_str = input('Enter PPD choice ([1]/2): ')    
if ppd_str.find('2') < 0:
    ppd_str = '1'

if ppd_str.find('2') < 0:
    # Get model file needed
    ppd_file = filedialog.askopenfilename(initialdir="U:\\Source Files\\Data Analytics\\Data-Science\\Data\\PPD\\",
                                          title="Choose the PPD file desired...")

    
init_save_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Phone_Quality_Model\\'
ppd_score_out_dir = filedialog.askdirectory(initialdir=init_save_dir,
                                         title="Choose directory to save the scored PPD in...")
ppd_score_out_dir = ppd_score_out_dir.replace("/", "\\")
ppd_score_out_dir += "\\"

ppd_archive_dir = ppd_score_out_dir + '_Archived\\'  
if not os.path.exists(ppd_archive_dir):
    os.mkdir(ppd_archive_dir)
  
  
# Get entity data
init_ent_comm_dir = 'C:\\'
ent_comm_file = filedialog.askopenfilename(initialdir=init_ent_comm_dir,
                                           title="Choose the entity_comm_at data csv file...")

ent_comm_usg_file = filedialog.askopenfilename(title="Choose the entity_comm_usg_at data csv file...")

phone_file = filedialog.askopenfilename(title="Choose the phone_at data csv file...")

license_file = filedialog.askopenfilename(title="Choose the license_lt data csv file...")

ent_key_file = filedialog.askopenfilename(title="Choose the entity_key_et data csv file...")

fone_zr_file = filedialog.askopenfilename(title="Choose the fone_zr data csv file...")
    
    
current_time = datetime.datetime.now()
start_time_str = current_time.strftime("%Y-%m-%d")


# Get PPD data
if ppd_str.find('2') < 0:
    ppd_df = pd.read_csv(ppd_file, delimiter = ",", index_col = None, header = 0, dtype = str)
    under_ndx = under_ndx = [i for i in range(len(ppd_file)) if ppd_file.startswith('_', i)]
    dot_ndx = ppd_file.find('.')
    ppd_date_str = ppd_file[under_ndx[-1] + 1:dot_ndx]
else:
    ppd_df, ppd_date_str = get_latest_ppd_data()
    
ppd_date = datetime.datetime.strptime(ppd_date_str, '%Y%m%d')


# Load entity data
ent_comm_df = pd.read_csv(ent_comm_file, delimiter=",", index_col=None, header=0, dtype=str, encoding='latin-1')
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


# Get latest model and variables
model_vars = pickle.load(open(model_var_file, 'rb'))
model = pickle.load(open(model_file, 'rb'))


ppd_scoring_df = create_ppd_scoring_data(ppd_df, ppd_date, ent_comm_df, ent_comm_usg_df, phone_df, 
                                         license_df, ent_key_df, fone_zr_df)

ppd_entity_file = ppd_archive_dir + start_time_str + '_PPD_' + ppd_date_str + '_Phone_Quality_PPD_Entity_Data.csv'
ppd_scoring_df.to_csv(ppd_entity_file, sep=',', header=True, index=True)

model_pred_df, model_data_pruned = score_phone_ppd_data(ppd_scoring_df, model, model_vars)
model_pred_df = model_pred_df.datalabs.rename_in_upper_case()

get_prob_info(model_pred_df['PRED_PROBABILITY'])
get_pred_info(model_pred_df['PRED_CLASS'])

ppd_dpc_output_file = ppd_score_out_dir + 'Phone_Quality_Scored_PPD_DPC_Pop.csv'
model_pred_df.to_csv(ppd_dpc_output_file, sep=',', header=True, index=True)

archived_output_file = ppd_archive_dir + start_time_str + '_PPD_' + ppd_date_str + '_Phone_Quality_Scored_PPD_DPC_Pop.csv'
model_pred_df.to_csv(archived_output_file, sep=',', header=True, index=True)

model_input_file = ppd_archive_dir + start_time_str + '_PPD_' + ppd_date_str + '_Phone_Quality_Input_Data.csv'
model_data_pruned.to_csv(model_input_file, sep=',', header=True, index=True)
        
