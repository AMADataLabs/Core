# Kari Palmier    7/31/19    Created
# Kari Palmier    8/14/19    Updated to work with more generic get_sample
#
#############################################################################
import datetime
import logging
import os
import pickle
import sys
import warnings

import pandas as pd

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


LOGGER.debug(f'PYTHONPATH: {os.environ["PYTHONPATH"]}')

### Import from Sandbox/CommonCode ###
# from get_ppd import get_latest_ppd_data
from capitalize_column_names import capitalize_column_names

### Import from Sandbox/CommonModelCode ###
from score_polo_addr_ppd_data import score_polo_ppd_data
from class_model_creation import get_prob_info, get_pred_info
from create_addr_model_input_data import create_ppd_scoring_data


warnings.filterwarnings("ignore")


# Get model file needed
# model_file = filedialog.askopenfilename(initialdir="U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Polo_Rank_Model\\",
#                                        title="Choose the current POLO address rank model sav file...")
model_file = os.environ['MODEL_FILE']
# Get model file needed
# model_var_file = filedialog.askopenfilename(title="Choose the current POLO address rank model feature list sav file...")
model_var_file = os.environ['MODEL_VAR_FILE']

# print('1 - Choose PPD csv file')
# print('2 - Use latest PPD')
# ppd_str = 1
# ppd_str = input('Enter PPD choice ([1]/2): ')
# if ppd_str.find('2') < 0:
#    ppd_str = '1'
#
# if ppd_str == '1':
#    # Get model file needed
#    ppd_file = filedialog.askopenfilename(initialdir="U:\\Source Files\\Data Analytics\\Data-Science\\Data\\PPD\\",
#                                          title="Choose the PPD file desired...")
ppd_file = os.environ['PPD_FILE']

init_save_dir = os.environ['INIT_SAVE_DIR']
# init_save_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Polo_Rank_Model\\'
# ppd_score_out_dir = filedialog.askdirectory(initialdir = init_save_dir,
#                                            title="Choose directory to save the scored PPD in...")
# ppd_score_out_dir = ppd_score_out_dir.replace("/", "\\")
# ppd_score_out_dir += "\\"
ppd_score_out_dir = init_save_dir

ppd_archive_dir = ppd_score_out_dir + '_Archived\\'
if not os.path.exists(ppd_archive_dir):
    os.mkdir(ppd_archive_dir)

##### # Get entity data
##### init_ent_comm_dir = 'C:\\'
##### ent_comm_file = filedialog.askopenfilename(initialdir=init_ent_comm_dir,
#####                                            title="Choose the entity_comm_at data csv file...")
#####
##### ent_comm_usg_file = filedialog.askopenfilename(title="Choose the entity_comm_usg_at data csv file...")
#####
##### post_addr_file = filedialog.askopenfilename(title="Choose the post_addr_at data csv file...")
#####
##### license_file = filedialog.askopenfilename(title="Choose the license_lt data csv file...")
#####
##### ent_key_file = filedialog.askopenfilename(title="Choose the entity_key_et data csv file...")


current_time = datetime.datetime.now()
start_time_str = current_time.strftime("%Y-%m-%d")

# Get PPD data
ppd_str = '1'
if ppd_str == '1':
    print('Loading PPD')
    ppd_df = pd.read_csv(ppd_file, dtype=str)
    # under_ndx = under_ndx = [i for i in range(len(ppd_file)) if ppd_file.startswith('_', i)]
    under_ndx = ppd_file.rindex('_')
    # dot_ndx = ppd_file.find('.')
    dot_ndx = ppd_file.index('.')
    # ppd_date_str = ppd_file[under_ndx[-1] + 1:dot_ndx]
    ppd_date_str = ppd_file[under_ndx + 1:dot_ndx]
else:
    # ppd_df, ppd_date_str = get_latest_ppd_data()
    quit()
ppd_date = datetime.datetime.strptime(ppd_date_str, '%Y%m%d')

# Load entity data
print('Loading entity data')
# ent_comm_df = pd.read_csv(ent_comm_file, delimiter=",", index_col=None, header=0, dtype=str)
ent_comm_df = pd.read_csv(os.environ['ENTITY_COMM_AT_FILE'], dtype=str, na_values=['', '(null)'])

# ent_comm_df['comm_cat'] = ent_comm_df['comm_cat'].apply(str.strip)
# ent_comm_df = ent_comm_df[ent_comm_df['comm_cat'] == 'A']
assert len(ent_comm_df) > 0
# ent_comm_usg_df = pd.read_csv(ent_comm_usg_file, delimiter=",", index_col = None, header=0, dtype=str)
ent_comm_usg_df = pd.read_csv(os.environ['ENTITY_COMM_USG_FILE'], dtype=str, na_values=['', '(null)'])
# ent_comm_usg_df['comm_cat'] = ent_comm_usg_df['comm_cat'].apply(str.strip)
# ent_comm_usg_df = ent_comm_usg_df[ent_comm_usg_df['comm_cat'] == 'A']
assert len(ent_comm_usg_df) > 0
# post_addr_df = pd.read_csv(post_addr_file, delimiter=",", index_col=None, header=0, dtype=str)
post_addr_df = pd.read_csv(os.environ['POST_ADDR_AT_FILE'], dtype=str, na_values=['', '(null)'])
# license_df = pd.read_csv(license_file, delimiter=",", index_col=None, header=0, dtype=str)
license_df = pd.read_csv(os.environ['LICENSE_LT_FILE'], dtype=str, na_values=['', '(null)'])
# ent_key_df = pd.read_csv(ent_key_file, delimiter=",", index_col=None, header=0, dtype=str)
ent_key_df = pd.read_csv(os.environ['ENTITY_KEY_ET_FILE'], dtype=str, na_values=['', '(null)'])

# Get latest model and variables
print('Loading model and variables')
model_vars = pickle.load(open(model_var_file, 'rb'))
model = pickle.load(open(model_file, 'rb'))

print('Creating scoring data')
ppd_scoring_df = create_ppd_scoring_data(ppd_df, ppd_date, ent_comm_df, ent_comm_usg_df, post_addr_df,
                                         license_df, ent_key_df)
print(len(ppd_scoring_df))
ppd_entity_file = ppd_archive_dir + start_time_str + '_PPD_' + ppd_date_str + '_Polo_Addr_Rank_PPD_Entity_Data.csv'
print('\tsaving scoring data to {}'.format(ppd_entity_file))
ppd_scoring_df.to_csv(ppd_entity_file, sep=',', header=True, index=True)

print('Applying model')
model_pred_df, model_data_pruned = score_polo_ppd_data(ppd_scoring_df, model, model_vars)
print('len model_pred_df', len(model_pred_df))
model_pred_df = capitalize_column_names(model_pred_df)
print('writing model_pred_df')
model_pred_df.to_csv(os.environ['MODEL_PREDICTIONS_FILE'], index=False)

model_pred_df['RANK_ROUND'] = model_pred_df['PRED_PROBABILITY'].apply(lambda x: round((x * 10)))
zero_ndx = model_pred_df['RANK_ROUND'] == 0
model_pred_df.loc[zero_ndx, 'RANK_ROUND'] = 1

print('Lenght of model_pred_df: {}'.format(len(model_pred_df)))
get_prob_info(model_pred_df['PRED_PROBABILITY'])
get_pred_info(model_pred_df['PRED_CLASS'])

ppd_dpc_output_file = ppd_score_out_dir + 'Polo_Addr_Rank_Scored_PPD_DPC_Pop.csv'
print('\tsaving predictions to {}'.format(ppd_score_out_dir))
model_pred_df.to_csv(ppd_dpc_output_file, sep=',', header=True, index=True)

archived_output_file = ppd_archive_dir + start_time_str + '_PPD_' + \
                       ppd_date_str + '_Polo_Addr_Rank_Scored_PPD_DPC_Pop.csv'
model_pred_df.to_csv(archived_output_file, sep=',', header=True, index=True)

model_input_file = ppd_archive_dir + start_time_str + '_PPD_' + ppd_date_str + '_Polo_Addr_Rank_Input_Data.csv'
model_data_pruned.to_csv(model_input_file, sep=',', header=True, index=True)
