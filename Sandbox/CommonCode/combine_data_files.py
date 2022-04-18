# Kari Palmier    Created 7/8/19
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

from select_files import select_files
from combine_data import combine_data

root = tk.Tk()
root.withdraw()

init_file_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\'
file_paths = select_files(init_file_dir, 'Select file(s) to combine')

out_dir = filedialog.askdirectory(title = "Choose directory to save in...")

out_dir = out_dir.replace("/", "\\")
out_dir += "\\"
print(out_dir)

out_name = input('Enter combined output file name: ')
out_file = out_dir + out_name
        
if out_file.find('.csv') < 0 and out_file.find('.xlsx') < 0:

    out_type = input('Enter the output file type ([csv] or xlsx): ')
    out_type = out_type.lower()
    if out_type.find('xlsx') < 0:
        out_type = 'csv'

    ext_ndx = out_file.find('.')
    if ext_ndx < 0:
        out_file += '.' + out_type
    else:
        out_file = out_file[:ext_ndx] + '.' + out_type


header_str = str(input("Does the data contain columns names in the first row? ([y]/n): "))
if header_str.lower().find('n') >= 0:
    header_row = None
else:
    header_row = 0

index_column = None
index_str = str(input("Does the data contain an index column on the far left? (y/[n]): "))
if index_str.lower().find('y') >= 0:
    index_column = 0
    out_index = True
else:
    index_column = None
    out_index = False


out_header = True
out_df = combine_data(file_paths, index_column, header_row)
    
if out_file.find('xlsx') >= 0 or out_file.find('xls') >= 0:
    writer = pd.ExcelWriter(out_file, engine = 'xlsxwriter')
    out_df.to_excel(writer, index = out_index, header = out_header)
    writer.save()
else:
    out_df.to_csv(out_file, sep = ',', index = out_index, header = out_header)
        

