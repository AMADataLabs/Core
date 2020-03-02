# Kari Palmier    Created 8/26/19
#
#############################################################################
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

from get_ppd import get_latest_ppd_data, get_ppd

import warnings
warnings.filterwarnings("ignore")


root = tk.Tk()
root.withdraw()

init_ppd_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\PPD\\'
ppd_out_dir = filedialog.askdirectory(initialdir=init_ppd_dir,
                                      title="Choose directory to save PPD csv output...")
ppd_out_dir = ppd_out_dir.replace("/", "\\")
ppd_out_dir += "\\"


ppd_type_str = input('Enter type of PPD: [1] = Latest, 2 = User Selected: ')
if ppd_type_str.find('2') < 0:
    ppd_type_str = '1'
    
if ppd_type_str == '1':
    print('Grabbing latest PPD...')
    ppd_df, ppd_date_str = get_latest_ppd_data()
    print('Done. Latest PPD date found: {}'.format(ppd_date_str))
else:
    init_ppd_dir = 'U:\\Source Files\\Data Analytics\\Baseline\\data\\'
    ppd_file = filedialog.askopenfilename(initialdir=init_ppd_dir,
                                          title="Choose the PPD file desired...")
    
    start_ndx = ppd_file.find('PhysicianProfessionalDataFile_') + len('PhysicianProfessionalDataFile_')
    end_name = ppd_file[start_ndx:]
    
    dot_ndx = end_name.find('.')
    if dot_ndx >= 0:
        end_name = end_name[:dot_ndx]
    
    under_ndx = end_name.find('_')
    if under_ndx >= 0:
        ppd_date_str = end_name[:under_ndx]

    slash_ndx = [i for i in range(len(ppd_file)) if ppd_file.startswith('/', i)]
    ppd_file_name = ppd_file[slash_ndx[-1]:]

    ppd_df = get_ppd(ppd_file_name)  
    
print('Writing to CSV.')
ppd_out_file = ppd_out_dir + 'ppd_data_' + ppd_date_str + '.csv'
ppd_df.to_csv(ppd_out_file, index=None, header=True)
print('Complete.')
