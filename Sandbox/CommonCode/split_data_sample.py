# Kari Palmier    7/18/19    Created
# Kari Palmier    8/16/19    Added saving printed information to log file
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

# Get model file needed
data_file = filedialog.askopenfilename(initialdir = "U:\\Source Files\\Data Analytics\\Data-Science\\Data\\",
                                         title = "Choose the file to sample...")

init_split_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\'
split_out_dir = filedialog.askdirectory(initialdir = init_split_dir,
                                         title = "Choose directory to save split output files...")
split_out_dir = split_out_dir.replace("/", "\\")
split_out_dir += "\\"

base_split_name = input('Input base name of output files: ')
dot_ndx = base_split_name.find('.')
if dot_ndx > 0:    
    base_split_name = base_split_name[:dot_ndx]

int_file_str = input('Do you want to include an internal file to sample the same? ([y]/n): ')
if int_file_str.find('n') >= 0:
    int_file = ''
else:
    int_file = filedialog.askopenfilename(initialdir = "U:\\Source Files\\Data Analytics\\Data-Science\\Data\\",
                                         title = "Choose the internal file...")
    

header_row = None
header_str = str(input("Does the data contain columns names in the first row? ([y]/n): "))
if header_str.lower().find('n') >= 0:
    header_row = None
    out_header = False
else:
    header_row = 0
    out_header = True

index_column = None
index_str = str(input("Does the data contain an index column on the far left? (y/[n]): "))
if index_str.lower().find('y') >= 0:
    index_column = 0
    out_index = True
else:
    index_column = None
    out_index = False

if data_file.find('.csv') > 0:
    data_df = pd.read_csv(data_file, delimiter = ",", index_col = index_column, header = header_row, dtype = str)
elif data_file.find('.xlsx') > 0 or data_file.find('.xls') > 0:
    data_df = pd.read_excel(data_file, index_col = index_column, header = header_row, dtype = str)
else:
    print("File type is not supported.")
    sys.exit()

if int_file != '':
    if int_file.find('.csv') > 0:
        int_data_df = pd.read_csv(int_file, delimiter = ",", index_col = index_column, header = header_row, dtype = str)
    elif int_file.find('.xlsx') > 0 or data_file.find('.xls') > 0:
        int_data_df = pd.read_excel(int_file, index_col = index_column, header = header_row, dtype = str)
    else:
        print("File type is not supported.")
        sys.exit()
        
    if (int_data_df.shape[0] != data_df.shape[0]):
        print('Internal and original sample files are not the same size.')
        sys.exit()
        
    int_data_df = int_data_df.set_index(data_df.index.values)

split_sizes = []
exit_loop = False
curr_total = 0
while not exit_loop:
    
    num_rows_left = data_df.shape[0] - curr_total
    
    print('\n')
    print('Number of rows in remaining dataset: {}'.format(num_rows_left))
    curr_split = int(input('Enter the size of the current sample desired: '))
    curr_total += curr_split
    split_sizes.append(curr_split)
    
    exit_str = input('Do you want to enter another sample from this file (y/[n])?: ')
    exit_str = exit_str.lower()
    
    if exit_str.find('y') < 0:
        exit_loop = True

data_list, data_index_list = split_data(data_df, split_sizes)

for i in range(len(data_index_list)):
    
    curr_ndx = data_index_list[i]  
    curr_df = data_df.loc[curr_ndx, :]
              
    if int_file != '':
        curr_int_df = int_data_df.loc[curr_ndx, :]

    split_name = split_out_dir + base_split_name + '_' + str(curr_df.shape[0]) + '_Part' + str(i)
    if data_file.find('.csv') >= 0:
        out_file = split_name + '.csv'       
        curr_df.to_csv(out_file, index = False, header = 0)       
        
        if int_file != '':
            int_out_file = split_name + '_Internal.csv'       
            curr_int_df.to_csv(int_out_file, sep = ',', index = False, header = 0)       
            
    else:
        out_file = split_name + '.xlsx'       
        writer = pd.ExcelWriter(out_file, engine = 'xlsxwriter')
        curr_df.to_excel(writer, index = False, header = True, na_rep = ' ')
        writer.save()

        if int_file != '':
            int_out_file = split_name + '_Internal.xlsx'       
            writer = pd.ExcelWriter(int_out_file, engine = 'xlsxwriter')
            curr_int_df.to_excel(writer, index = False, header = True, na_rep = ' ')
            writer.save()

