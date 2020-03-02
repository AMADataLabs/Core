# Kari Palmier    7/18/19    Created
# Kari Palmier    8/16/19    Added saving printed information to log file
#
#############################################################################

import pandas as pd
import tkinter as tk
from tkinter import filedialog
import sys


root = tk.Tk()
root.withdraw()

# Get model file needed
data_file = filedialog.askopenfilename(initialdir = "U:\\Source Files\\Data Analytics\\Data-Science\\Data\\",
                                         title = "Choose the file to sample...")

init_save_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Survey_Samples\\'
out_dir = filedialog.askdirectory(initialdir = init_save_dir,
                                         title = "Choose directory to save sample in...")
out_dir = out_dir.replace("/", "\\")
out_dir += "\\"

out_name = input('Enter sample output file name: ')
out_file = out_dir + out_name
        
out_type = input('Enter the output file type ([csv] or xlsx): ')
out_type = out_type.lower()
if out_type.find('xlsx') < 0:
    out_type = 'csv'

if out_file.find('.csv') < 0 and out_file.find('.xlsx') < 0:
    ext_ndx = out_file.find('.')
    if ext_ndx < 0:
        out_file += '.' + out_type
    else:
        out_file = out_file[:ext_ndx] + '.' + out_type
        
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

sample_str = input('Enter the sample size (all = all samples in bin): ')
if sample_str.lower() == 'all' or not(sample_str.isnumeric()):
    sample_size = 'all'
else:
    sample_size = int(sample_str)


if data_file.find('.csv') > 0:
    data_df = pd.read_csv(data_file, delimiter = ",", index_col = index_column, header = header_row, dtype = str)
elif data_file.find('.xlsx') > 0 or data_file.find('.xls') > 0:
    data_df = pd.read_excel(data_file, index_col = index_column, header = header_row, dtype = str)
else:
    print("File type is not supported.")
    sys.exit()

if int_file != '':
    if int_file.find('.csv') > 0:
        int_data_df = pd.read_csv(data_file, delimiter = ",", index_col = index_column, header = header_row, dtype = str)
    elif int_file.find('.xlsx') > 0 or data_file.find('.xls') > 0:
        int_data_df = pd.read_excel(data_file, index_col = index_column, header = header_row, dtype = str)
    else:
        print("File type is not supported.")
        sys.exit()
        
    if (int_data_df.shape[0] != data_df.shape[0]):
        print('Internal and original sample files are not the same size.')
        sys.exit()

    int_data_df = int_data_df.set_index(data_df.index.values)


if sample_size == 'all':
    sample_df = data_df
else:
    sample_ndx = data_df.sample(sample_size).index
    sample_df = data_df.loc[sample_ndx, :]
    
if out_file.find('xlsx') >= 0 or out_file.find('xls') >= 0:
    writer = pd.ExcelWriter(out_file, engine = 'xlsxwriter')
    sample_df.to_excel(writer, index = out_index, header = out_header)
    writer.save()
else:
    sample_df.to_csv(out_file, sep = ',', index = out_index, header = out_header)

if int_file != '':
    int_sample_df = int_data_df.loc[sample_ndx, :]
    
    dot_ndx = out_file.index('.')
    int_out_file = out_file[:dot_ndx] + '_Internal' + out_file[dot_ndx:]
    
    if int_out_file.find('xlsx') >= 0 or int_out_file.find('xls') >= 0:
        writer = pd.ExcelWriter(int_out_file, engine = 'xlsxwriter')
        int_sample_df.to_excel(writer, index = out_index, header = out_header)
        writer.save()
    else:
        int_sample_df.to_csv(int_out_file, sep = ',', index = out_index, header = out_header)
    
