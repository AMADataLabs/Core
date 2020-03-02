# Kari Palmier    10/16/19    Created
#
#############################################################################
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import datetime

import warnings
warnings.filterwarnings("ignore")

root = tk.Tk()
root.withdraw()


init_sample_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Survey_Samples\\Standard\\'
# Get model file needed
sample_file = filedialog.askopenfilename(initialdir = init_sample_dir,
                                         title = "Choose the standard sample file...")
sample_file = sample_file.replace("/", "\\")


out_dir = filedialog.askdirectory(initialdir = init_sample_dir,
                                         title = "Choose directory to save sample in...")
out_dir = out_dir.replace("/", "\\")
out_dir += "\\"


init_ent_comm_dir = 'C:\\'
ent_comm_usg_file = filedialog.askopenfilename(title = \
                                         "Choose the entity_comm_usg_at data csv file...")

email_file = filedialog.askopenfilename(title = \
                                            "Choose the email_at data csv file...")

ent_key_file = filedialog.askopenfilename(title = \
                                            "Choose the entity_key_et data csv file...")

num_w_email = int(input('Enter the number of samples with emails: '))
num_no_email = int(input('Enter the number of samples without emails: '))


current_time = datetime.datetime.now()
start_time_str = current_time.strftime("%Y-%m-%d")


sample_df =  pd.read_excel(sample_file, index_col = None, header = 0, dtype = str)


# Load entity data
ent_comm_usg_df = pd.read_csv(ent_comm_usg_file, delimiter = ",", index_col = None, header = 0, dtype = str)
ent_comm_usg_df = ent_comm_usg_df[ent_comm_usg_df['comm_usage'] == 'PE']
ent_comm_usg_df = ent_comm_usg_df[ent_comm_usg_df['end_dt'].isna()]

email_df = pd.read_csv(email_file, delimiter = ",", index_col = None, header = 0, dtype = str)
ent_key_df = pd.read_csv(ent_key_file, delimiter = ",", index_col = None, header = 0, dtype = str)


ent_usg_me_df = ent_comm_usg_df.merge(ent_key_df, how = 'inner', on = 'entity_id')
ent_usg_email_df = ent_usg_me_df.merge(email_df, how = 'inner', on = 'comm_id')
ent_usg_email_df['email_addr'] = ent_usg_email_df['user_nm'] + '@' + ent_usg_email_df['domain']

sample_ent_df = sample_df.merge(ent_usg_email_df, how = 'left', left_on = 'ME', right_on = 'key_type_val')

sample_email_df = sample_ent_df[sample_ent_df['email_addr'].notnull()]
sample_no_email_df = sample_ent_df[sample_ent_df['email_addr'].isna()]


# If number with email is greater than actual number with email present, fill in rest with no email entries
num_wo_needed = 0
if sample_email_df.shape[0] < num_w_email:
    num_wo_needed = num_w_email - sample_email_df.shape[0]


sample_email_ndx = sample_email_df.sample(num_w_email).index
email_sample_out_df = sample_email_df.loc[sample_email_ndx, :]

if num_wo_needed > 0:
    no_email_add_ndx = sample_no_email_df.sample(num_wo_needed).index
    email_sample_out_df = pd.concat([email_sample_out_df, sample_no_email_df.loc[no_email_add_ndx, :]])
    
    sample_no_email_df = sample_no_email_df[~no_email_add_ndx]
    
sample_no_email_ndx = sample_no_email_df.sample(num_no_email).index
no_email_sample_out_df = sample_no_email_df.loc[sample_no_email_ndx, :]


orig_out_cols = list(sample_df.columns.values)
email_out_cols = list(orig_out_cols)
email_out_cols.append('email_addr')
email_sample_out_df = email_sample_out_df[email_out_cols]
no_email_sample_out_df = no_email_sample_out_df[orig_out_cols]

email_sample_out_df = email_sample_out_df.rename(columns = {'email_addr':'EMAIL'})
slash_ndx = [i for i in range(len(sample_file)) if sample_file.startswith('\\', i)]
orig_name = sample_file[slash_ndx[-1]:]
dot_ndx = orig_name.find('.')
base_name = orig_name[:dot_ndx]

outfile_w_email = out_dir + base_name + '_WithEmails.xlsx'
writer = pd.ExcelWriter(outfile_w_email, engine = 'xlsxwriter')
email_sample_out_df.to_excel(writer, index = False, header = True)
writer.save()
        
if no_email_sample_out_df.shape[0] > 0:
    outfile_wo_email = out_dir + base_name + '_NoEmail.xlsx'
    writer = pd.ExcelWriter(outfile_wo_email, engine = 'xlsxwriter')
    no_email_sample_out_df.to_excel(writer, index = False, header = True)
    writer.save()








