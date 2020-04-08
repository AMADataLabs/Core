# Kari Palmier    9/9/19    Created
#
#############################################################################
import datetime
import os
import sys
import tkinter as tk
from tkinter import filedialog
import warnings

import settings
from get_ddb_logins import get_ddb_logins
from get_ods_db_tables import get_iqvia_all_phys_info
from   datalabs.access.ods import ODS

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

ods = ODS()
ods.connect()

iqvia_df = get_iqvia_all_phys_info(ods._connection)

ods.close()

out_file = out_dir + start_time_str + '_IQVIA_Data.csv'
iqvia_df.to_csv(out_file, index=False, header=True)
