# Kari Palmier    9/9/19    Created
#
#############################################################################
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

from get_ddb_logins import get_ddb_logins
from get_ods_db_tables import get_iqvia_all_phys_info, get_ods_connection

import warnings
warnings.filterwarnings("ignore")


root = tk.Tk()
root.withdraw()

# Get files needed
ddb_info_file = filedialog.askopenfilename(initialdir="C:\\",
                                           title="Choose txt file with database login information...")

init_save_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\IQVIA\\'
out_dir = filedialog.askdirectory(initialdir=init_save_dir,
                                  title="Choose directory to save data in...")
out_dir = out_dir.replace("/", "\\")
out_dir += "\\"

current_time = datetime.datetime.now()
start_time_str = current_time.strftime("%Y-%m-%d")

# Get ddb login information
ddb_login_dict = get_ddb_logins(ddb_info_file)

if 'ODS' not in ddb_login_dict.keys():
    print('ODS login information not present.')
    sys.exit()

ODS_conn = get_ods_connection(ddb_login_dict['ODS']['username'], ddb_login_dict['ODS']['password'])

iqvia_df = get_iqvia_all_phys_info(ODS_conn)

ODS_conn.close()

out_file = out_dir + start_time_str + '_IQVIA_Data.csv'
iqvia_df.to_csv(out_file, index=False, header=True)
