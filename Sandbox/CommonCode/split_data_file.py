# Kari Palmier    Created 8/15/19
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

from split_data import split_data

import warnings
warnings.filterwarnings("ignore")


root = tk.Tk()
root.withdraw()

init_split_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\'
split_file = filedialog.askopenfilename(initialdir = init_split_dir,
                                         title = "Choose split file to split...")

split_out_dir = filedialog.askdirectory(initialdir = init_split_dir,
                                         title = "Choose directory to save split output files...")
split_out_dir = split_out_dir.replace("/", "\\")
split_out_dir += "\\"

base_split_name = input('Input base name of output files: ')
dot_ndx = base_split_name.find('.')
if dot_ndx > 0:    
    base_split_name = base_split_name[:dot_ndx]

# Read in VT response data
if split_file.find('.csv') >= 0:
    orig_split_df = pd.read_csv(split_file, delimiter = ",", index_col = None, header = 0, dtype = 'object')
else:
    orig_split_df = pd.read_excel(split_file, index_col = None, header = 0, dtype = 'object')

split_sizes = []
exit_loop = False
curr_total = 0
while not exit_loop:
    
    num_rows_left = orig_split_df.shape[0] - curr_total
    
    print('\n')
    print('Number of rows in remaining dataset: {}'.format(num_rows_left))
    curr_split = int(input('Enter the size of the current sample desired: '))
    curr_total += curr_split
    split_sizes.append(curr_split)
    
    exit_str = input('Do you want to enter another sample from this file (y/[n])?: ')
    exit_str = exit_str.upper()
    
    if exit_str.find('Y') < 0:
        exit_loop = True
   

data_list, data_index_list = split_data(orig_split_df, split_sizes)

for i in range(len(data_list)):
    
    curr_df = data_list[i]  
           
    if split_file.find('.csv') >= 0:
        out_file = split_out_dir + base_split_name + '_' + str(curr_df.shape[0]) + '.csv'       
        curr_df.to_csv(out_file, sep = ',', index = False, header = 0)       
    else:
        out_file = split_out_dir + base_split_name + '_' + str(curr_df.shape[0]) + '.xlsx'       
        writer = pd.ExcelWriter(out_file, engine = 'xlsxwriter')
        curr_df.to_excel(writer, index = False, header = True, na_rep = ' ')
        writer.save()
