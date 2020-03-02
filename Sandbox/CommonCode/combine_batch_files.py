# Kari Palmier    Created 8/15/19
#
#############################################################################
import pandas as pd
import datetime
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

from create_batch_loads import combine_batches
from select_files import select_files

import warnings
warnings.filterwarnings("ignore")


current_time = datetime.datetime.now()
day_str = current_time.strftime("%Y%m%d")

root = tk.Tk()
root.withdraw()

init_batch_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\IT_BatchLoads\\'
batch_files = select_files(init_batch_dir, 'Select batch file(s) to combine')


batch_out_dir = filedialog.askdirectory(initialdir = init_batch_dir,
                                         title = "Choose directory to save combined output file...")
batch_out_dir = batch_out_dir.replace("/", "\\")
batch_out_dir += "\\"

combined_out_file = input('Enter name of combined output file: ')
if combined_out_file.find('.csv') < 0:
    dot_ndx = combined_out_file.find('.')
    if dot_ndx >= 0:
         combined_out_file = combined_out_file[0:dot_ndx] + '.csv'
    else:
         combined_out_file = combined_out_file + '.csv'

combined_out_file = batch_out_dir + combined_out_file

phone_fax_input = input('Enter the type of phone numbers in the batch files ([1] = phone, 2 = fax): ')
   
if phone_fax_input.strip() != '2':
    phone_fax_var = 'phone'
else:
    phone_fax_var = 'fax'
    
for i in range(len(batch_files)):
    
    temp_df = pd.read_csv(batch_files[i], delimiter = ",", index_col = None, header = 0, dtype = str)
    batch_cols = list(temp_df.columns.values)
    batch_col_map = {'office_phone':'phone', 'office_fax':'fax'}
    if 'office_phone' in batch_cols:
        temp_df = temp_df.rename(columns = batch_col_map)
   
    if i == 0:
        combined_df = temp_df[:]
    else:
        combined_df = combine_batches(combined_df, temp_df, phone_fax_var)
    
    
combined_df.to_csv(combined_out_file, index = False, header = True)



