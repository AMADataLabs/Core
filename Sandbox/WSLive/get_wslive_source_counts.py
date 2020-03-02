# Kari Palmier    Created 8/8/19
# Kari Palmier    Updated to filter known bad by if they are in current PPD
#
#############################################################################
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import datetime

# Get path of general (common) code and add it to the python path variable
import sys
import os
curr_path = os.path.abspath(__file__)
slash_ndx = [i for i in range(len(curr_path)) if curr_path.startswith('\\', i)]
base_path = curr_path[:slash_ndx[-2]+1]
gen_path = base_path + 'Common_Code\\'
sys.path.insert(0, gen_path)

from get_input_date_range import get_input_date_range
from select_files import select_files
from combine_data import combine_data
from capitalize_column_names import capitalize_column_names

import warnings
warnings.filterwarnings("ignore")

 
root = tk.Tk()
root.withdraw()

init_wslive_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\WSLive\\'
wslive_results_file = filedialog.askopenfilename(initialdir = init_wslive_dir,
                                         title = "Choose WSLive file with results encoded...")

print('\n\n')
smpl_str = input('Do you want to match results to samples sent? (y/[n]): ')
smpl_str = smpl_str.lower()
if smpl_str.find('y') < 0:
    smpl_str = 'n'
    
sample_paths = []
if smpl_str == 'y':
    init_sample_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Survey_Samples\\'
    sample_paths = select_files(init_sample_dir, 'Select file(s) from standard survey')

    
start_date, end_date, date_range_str = get_input_date_range()

current_time = datetime.datetime.now()
start_time_str = current_time.strftime("%Y-%m-%d")

# Read in samples sent
if len(sample_paths) > 0:
    sample_df = combine_data(sample_paths, None, 0)
    sample_df = capitalize_column_names(sample_df)

# Read in wslive data
wslive_results_df = pd.read_csv(wslive_results_file, delimiter = ",", index_col = None, header = 0, dtype = str)
wslive_results_df = capitalize_column_names(wslive_results_df)

# Get data for date range specified
wslive_results_df['WSLIVE_FILE_DT'] = pd.to_datetime(wslive_results_df['WSLIVE_FILE_DT'])
wslive_res_date_df = wslive_results_df[(wslive_results_df['WSLIVE_FILE_DT'] >= start_date) & \
                                  (wslive_results_df['WSLIVE_FILE_DT'] <= end_date)]
            
# Join results with sample sent on ME
if len(sample_paths) > 0:
    wslive_res_smpl_df = wslive_res_date_df.merge(sample_df, how = 'inner', 
                                                  left_on = ['PHYSICIAN_ME_NUMBER',
                                                             'OFFICE_TELEPHONE'],
                                                 right_on = ['ME', 'TELEPHONE_NUMBER'])
else:
    wslive_res_smpl_df = wslive_results_df

print('\n')
print('Standard Survey Result Counts')
print('-----------------------------')

# Loop over source types and compile results for each
survey_sources = [['C', 'Z'], 'CR', 'CA', 'CB', 'Q', 'S', 'VT']
survey_names = ['MF', 'MF Random', 'MF Risky W Email', 'MF Risky No Email', 
                'IQVIA', 'Symphony', 'Vertical Trail']

for i in range(len(survey_sources)):
    
    source_code = survey_sources[i]
    survey_name = survey_names[i]
        
    # If source type for MF is a list so need to treat differently
    if type(source_code).__name__ == 'list':
        source_ndx = wslive_res_smpl_df['SOURCE'].isin(source_code)
    else:
        source_ndx = wslive_res_smpl_df['SOURCE'] == source_code
        
    print('{} Count: {}'.format(survey_name, sum(source_ndx)))
        

 
