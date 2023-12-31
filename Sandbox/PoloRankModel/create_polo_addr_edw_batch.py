# Kari Palmier    Created 8/26/19
#
#############################################################################
import os
import sys
import datetime
import tkinter as tk
from tkinter import filedialog
import warnings

import pandas as pd

import settings
from   datalabs.access.edw import EDW
import datalabs.curate.dataframe  # pylint: disable=unused-import

warnings.filterwarnings("ignore")

    
root = tk.Tk()
root.withdraw()

# Get files needed
ddb_info_file = filedialog.askopenfilename(initialdir = "C:\\",
                                         title = "Choose txt file with database login information...")

init_rank_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Polo_Rank_Model\\'
ranked_file = filedialog.askopenfilename(initialdir = init_rank_dir,
                                         title = "Choose the file with the ranked data...")   
    
init_out_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\IT_BatchLoads\\POLO_Ranking\\'
out_dir = filedialog.askdirectory(initialdir = init_out_dir,
                                         title = "Choose directory to save batch output...")
out_dir = out_dir.replace("/", "\\")
out_dir += "\\"


ranked_df = pd.read_csv(ranked_file, delimiter = ",", index_col = None, header = 0, dtype = str)
ranked_df = ranked_df.datalabs.rename_in_upper_case()


with EDW() as edw:
    party_key_df = edw.get_me_numbers()
    addr_df = edw.get_postal_address_map()


ranked_df = ranked_df.merge(party_key_df, how = 'inner', left_on = 'PPD_ME', right_on = 'KEY_VAL')

addr_df['SRC_POST_KEY'] = addr_df['SRC_POST_KEY'].astype(str)
addr_df['SRC_POST_KEY'] = addr_df['SRC_POST_KEY'].apply(lambda x: x[:-2] if x.find('.0') > 0 else x)
ranked_df = ranked_df.merge(addr_df, how = 'inner', left_on = 'ENT_COMM_COMM_ID', right_on = 'SRC_POST_KEY')


batch_df = ranked_df[['PARTY_ID', 'POST_CD_ID', 'RANK_ROUND']]
uniq_batch_df = batch_df.groupby(['PARTY_ID', 'POST_CD_ID']).first().reset_index()

current_time = datetime.datetime.now()

uniq_batch_df['AS_OF_DT'] = current_time.strftime('%m/%d/%y')

uniq_batch_df = uniq_batch_df.rename(columns = {'RANK_ROUND':'ADDR_SCORE'})

uniq_batch_df = uniq_batch_df[['PARTY_ID', 'POST_CD_ID', 'AS_OF_DT', 'ADDR_SCORE']]


out_name = out_dir + current_time.strftime('%Y-%m-%d') + '_EDW_PoloRank_Batch.csv'
uniq_batch_df.to_csv(out_name, sep = ',', header = True, index = False)



    
