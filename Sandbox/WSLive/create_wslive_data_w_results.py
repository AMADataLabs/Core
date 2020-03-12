# Kari Palmier    Created 8/26/19
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
gen_path = base_path + 'CommonCode\\'
sys.path.insert(0, gen_path)

from get_input_date_range import get_input_date_range

import warnings
warnings.filterwarnings("ignore")

    
root = tk.Tk()
root.withdraw()

print('1 - Read from SAS file')
print('2 - Read from CSV or Excel file')
source_type = input('Choose source type ([1]/2): ')
if source_type.find('2') < 0:
    source_type = '1'

# WHY DO THIS WHEN THERE"S ONLY ONE FILE COME ON
init_wslive_out_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\WSLive\\'
if source_type == '1':
    init_sas_dir = 'U:\\Source Files\\Data Analytics\\Derek\\SAS_DATA\SURVEY\\'
    sas_result_file = filedialog.askopenfilename(initialdir=init_sas_dir,
                                                 title="Choose latest wslive_results.sas7bdat ...")
else:
    wslive_result_file = filedialog.askopenfilename(initialdir=init_wslive_out_dir,
                                                    title="Choose the CSV or Excel WSLive result file...")
# fixed for ya
# sas_result_file = 'U:\\Source Files\\Data Analytics\\Derek\\SAS_DATA\SURVEY\\wslive_results.sas7bdat'

init_wslive_out_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\WSLive\\'
wslive_out_dir = filedialog.askdirectory(initialdir=init_wslive_out_dir,
                                         title="Choose directory to save WSLive with results output...")
wslive_out_dir = wslive_out_dir.replace("/", "\\")
wslive_out_dir += "\\"


time_str = input('Do you want to choose a time subset (n will save all data)? ([y]/n): ')

if time_str.lower().find('n') >= 0:
    date_range_str = ''
else:
    start_date, end_date, date_range_str = get_input_date_range()


if source_type == '1':
    # Read in wslive data
    wslive_results_df = pd.read_sas(sas_result_file, format='sas7bdat', index=None, encoding='IBM437')
else:
    if wslive_result_file.find('.csv') > 0:
        wslive_results_df = pd.read_csv(wslive_result_file, delimiter=",", index_col=None, header=0, dtype=str)
    elif wslive_result_file.find('.xlsx') > 0 or wslive_result_file.find('.xls') > 0:
        wslive_results_df = pd.read_excel(wslive_result_file, index_col=None, header=0, dtype=str)
    else:
        del_str = str(input(
                "File type selected is not a csv or Excel file.  Is the file delimited by a different char? (y/n): "))
        if del_str.lower().find('y') >= 0:
            del_type = str(input("Enter the file delimiter (\t for tab for example): "))
            wslive_results_df = pd.read_csv(wslive_result_file, delimiter=del_type, index_col=None,
                                  header=0, dtype=str)
        else:
            print("File type is not supported.")
            sys.exit()


wslive_results_df['WSLIVE_FILE_DT'] = pd.to_datetime(wslive_results_df['WSLIVE_FILE_DT'])
wslive_results_df['ws_month'] = wslive_results_df['WSLIVE_FILE_DT'].apply(lambda x: x.month if x != None else x) 
wslive_results_df['ws_year'] = wslive_results_df['WSLIVE_FILE_DT'].apply(lambda x: x.year if x != None else x)

if date_range_str != '':
    wslive_date_df = wslive_results_df[(wslive_results_df['WSLIVE_FILE_DT'] >= start_date) &
                                       (wslive_results_df['WSLIVE_FILE_DT'] <= end_date)]
else:
    wslive_date_df = wslive_results_df[:]


wslive_date_df['new_metric'] = 'Inconclusive'

update_ndx = wslive_date_df['WSLIVE_SOURCE'] == 'UPDATED'
kd_ndx = (wslive_date_df['WSLIVE_SOURCE'] == 'OTHERS') & (wslive_date_df['COMMENTS'].isin(['DISCONNECT', 'NOT IN SERVICE', 
                       'WRONG NUMBER', 'RETIRED', 'DECEASED', 'FAX MODEM', 'FAX OR MODEM LINE', 'MOVED, NO FORWARDING INFO']))
nc_ndx = wslive_date_df['WSLIVE_SOURCE'] == 'FAIL'

wslive_date_df.loc[update_ndx, 'new_metric'] = 'Updated'
wslive_date_df.loc[kd_ndx, 'new_metric'] = 'Known Bad'
wslive_date_df.loc[nc_ndx, 'new_metric'] = 'No Contact'


wslive_date_df['addr_status'] = wslive_date_df['new_metric']
addr_conf_ndx = (wslive_date_df['addr_status'] == 'Updated') & (wslive_date_df['OFFICE_ADDRESS_VERIFIED_UPDATED'] == '1')
wslive_date_df.loc[addr_conf_ndx, 'addr_status'] = 'Confirmed'

wslive_date_df['pe_status'] = wslive_date_df['new_metric']
pe_conf_ndx = (wslive_date_df['pe_status'] == 'Updated') & (wslive_date_df['PRESENT_EMPLOYMENT_UPDATED'] == '1')
wslive_date_df.loc[pe_conf_ndx, 'pe_status'] = 'Confirmed'

wslive_date_df['phone_status'] = wslive_date_df['new_metric']
phone_conf_ndx = (wslive_date_df['phone_status'] == 'Updated') & (wslive_date_df['OFFICE_PHONE_VERIFIED_UPDATED'] == '1')
wslive_date_df.loc[phone_conf_ndx, 'phone_status'] = 'Confirmed'

wslive_date_df['fax_status'] = wslive_date_df['new_metric']
fax_conf_ndx = (wslive_date_df['fax_status'] == 'Updated') & (wslive_date_df['OFFICE_FAX_VERIFIED_UPDATED'] == '1')
wslive_date_df.loc[fax_conf_ndx, 'fax_status'] = 'Confirmed'

wslive_date_df['spec_status'] = wslive_date_df['new_metric']
spec_conf_ndx = (wslive_date_df['spec_status'] == 'Updated') & (wslive_date_df['SPECIALTY_UPDATED'] == '1')
wslive_date_df.loc[spec_conf_ndx, 'spec_status'] = 'Confirmed'


min_date = wslive_date_df['WSLIVE_FILE_DT'].min()
min_time_str = min_date.strftime("%Y-%m-%d")

max_date = wslive_date_df['WSLIVE_FILE_DT'].max()
max_time_str = max_date.strftime("%Y-%m-%d")
         

wslive_out_file = wslive_out_dir + 'wslive_with_results_' +  min_time_str + '_to_' + max_time_str + '.csv'
wslive_date_df.to_csv(wslive_out_file, index=None, header=True)

