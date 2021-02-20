import datetime
import os
import sys
import tkinter as tk
from tkinter import filedialog
import warnings

import pandas as pd

import settings
from get_aims_db_tables import get_ent_comm_phones, get_comm_usg_all_phones
from select_files import select_files
from datalabs.access.aims import AIMS

warnings.filterwarnings("ignore")


root = tk.Tk()
root.withdraw()

init_ppd_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\PPD\\'
ppd_file = filedialog.askopenfilename(initialdir = init_ppd_dir,
                                         title = "Choose latest PPD CSV file...")

# Get files needed
ddb_info_file = filedialog.askopenfilename(initialdir = "C:\\",
                                         title = "Choose txt file with database login information...")

init_anlys_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\PPD\\Analysis\\'
anlys_out_dir = filedialog.askdirectory(initialdir = init_anlys_dir,
                                         title = "Choose directory to save analysis output...")
anlys_out_dir = anlys_out_dir.replace("/", "\\")
anlys_out_dir += "\\"

support_dir = anlys_out_dir + 'Support\\'
if not os.path.exists(support_dir):
    os.mkdir(support_dir)


init_batch_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\IT_BatchLoads\\'
batch_file_paths = select_files(init_batch_dir, 'Choose batch file(s) to analyze')


# Get current date for output file names
current_time = datetime.datetime.now()
start_time_str = current_time.strftime("%Y-%m-%d")

# Create log file
old_stdout = sys.stdout
log_filename = anlys_out_dir + start_time_str + '_PPD_Bad_Phone_Analysis_Log.txt'
log_file = open(log_filename, "w")
sys.stdout = log_file

    
# Read PPD and find only non-null TELEPHONE NUMBER entries
ppd_df = pd.read_csv(ppd_file, delimiter = ",", index_col = None, header = 0, dtype = str)
ppd_not_null_df = ppd_df[ppd_df['TELEPHONE_NUMBER'].notnull()]

# get entity_comm_at, phone_at, and me info for latest begin date of each me/entity_id
with AIMS() as aims:
    entity_comm_me_df = get_ent_comm_phones(aims._connection)
    entity_comm_me_usg_df = get_comm_usg_all_phones(aims._connection)
    entity_me_usg_pv_df = entity_comm_me_usg_df[entity_comm_me_usg_df['comm_usage'] == 'PV']

entity_uniq_df = entity_comm_me_df.sort_values(['begin_dt'], ascending = False).groupby(['me', 
                                              'aims_phone']).first().reset_index()

entity_uniq_usg_df = entity_comm_me_usg_df.sort_values(['usg_begin_dt'], ascending = False).groupby(['me', 
                                                      'aims_phone']).first().reset_index()

entity_uniq_usg_pv_df = entity_me_usg_pv_df.sort_values(['usg_begin_dt'], ascending = False).groupby(['me', 
                                                       'aims_phone']).first().reset_index()

total_count = 0
for i in range(len(batch_file_paths)):
        
    file = batch_file_paths[i]
    print('---------------------------------------------------------------------------------------------------------')
    print('Current batch file: {}'.format(file))
    print('---------------------------------------------------------------------------------------------------------')
    
    temp_df = pd.read_csv(file, delimiter = ",", index_col = None, header = 0, dtype = str)
    batch_cols = list(temp_df.columns.values)
    batch_col_map = {'office_phone':'phone', 'office_fax':'fax'}
    if 'office_phone' in batch_cols:
        temp_df = temp_df.rename(columns = batch_col_map)
   
    num_temp = temp_df.shape[0]
    print('Number of batch records in current file: {}: '.format(num_temp))
    print('\n')
    
    total_count += num_temp
    
    temp_entity_df = temp_df.merge(entity_uniq_df, how = 'inner', left_on = ['me', 'phone'], right_on = ['me', 'aims_phone'])
    
    num_null_end = sum(temp_entity_df['end_dt'].isna())
    num_w_end = sum(temp_entity_df['end_dt'].notnull())
    
    print('Number batch records with matching entity_comm_at me and phone: {}: '.format(temp_entity_df.shape[0]))
    print('Number of batch records with null entity_comm_at ent_dt: {}'.format(num_null_end))
    print('Number of batch records with entity_comm_at ent_dt present: {}'.format(num_w_end))
    print('\n')

    temp_entity_usg_df = temp_df.merge(entity_uniq_usg_df, how = 'inner', left_on = ['me', 'phone'], 
                                       right_on = ['me', 'aims_phone'])
    
    num_null_end_usg = sum(temp_entity_usg_df['end_dt'].isna())
    num_w_end_usg = sum(temp_entity_usg_df['end_dt'].notnull())
    
    print('Number batch records with matching entity_comm_usg_at me and phone: {}: '.format(temp_entity_usg_df.shape[0]))
    print('Number of batch records with null entity_comm_usg_at ent_dt: {}'.format(num_null_end_usg))
    print('Number of batch records with entity_comm_usg_at ent_dt present: {}'.format(num_w_end_usg))
    print('\n')
    
    temp_entity_usg_pv_df = temp_df.merge(entity_uniq_usg_pv_df, how = 'inner', left_on = ['me', 'phone'], 
                                          right_on = ['me', 'aims_phone'])
    
    num_null_end_usg_pv = sum(temp_entity_usg_pv_df['end_dt'].isna())
    num_w_end_usg_pv = sum(temp_entity_usg_pv_df['end_dt'].notnull())
    
    print('Number batch records with matching entity_comm_usg_at PV me and phone: {}: '.format(temp_entity_usg_pv_df.shape[0]))
    print('Number of batch records with null entity_comm_usg_at PV ent_dt: {}'.format(num_null_end_usg_pv))
    print('Number of batch records with entity_comm_usg_at ent_dt PV present: {}'.format(num_w_end_usg_pv))
    print('\n')
    

    if i == 0:
        combined_ent_df = temp_entity_df[:]
        combined_ent_usg_df = temp_entity_usg_df[:]
        combined_ent_usg_pv_df = temp_entity_usg_pv_df[:]
    else:
        combined_ent_df = pd.concat([combined_ent_df, temp_entity_df])
        combined_ent_usg_df = pd.concat([combined_ent_usg_df, temp_entity_usg_df])
        combined_ent_usg_pv_df = pd.concat([combined_ent_usg_pv_df, temp_entity_usg_pv_df])
    
    file = file.replace("/", "\\")
    slash_ndx = [i for i in range(len(file)) if file.startswith('\\', i)]
    base_name = file[slash_ndx[-1]+1:]
    dot_ndx = base_name.find('.')
    
    temp_anlys_out_file = support_dir + base_name[:dot_ndx] + '_W_EntityInfo' + base_name[dot_ndx:]
    temp_entity_df.to_csv(temp_anlys_out_file, index = False, header = True)

    temp_usg_anlys_out_file = support_dir + base_name[:dot_ndx] + '_W_EntityUsgInfo' + base_name[dot_ndx:]
    temp_entity_usg_df.to_csv(temp_usg_anlys_out_file, index = False, header = True)

    temp_usg_pv_anlys_out_file = support_dir + base_name[:dot_ndx] + '_W_EntityUsgPreferredInfo' + base_name[dot_ndx:]
    temp_entity_usg_pv_df.to_csv(temp_usg_pv_anlys_out_file, index = False, header = True)


total_no_end = sum(combined_ent_df['end_dt'].isna())
total_w_end = sum(combined_ent_df['end_dt'].notnull())

total_no_end_usg = sum(combined_ent_usg_df['end_dt'].isna())
total_w_end_usg = sum(combined_ent_usg_df['end_dt'].notnull())

total_no_end_usg_pv = sum(combined_ent_usg_pv_df['end_dt'].isna())
total_w_end_usg_pv = sum(combined_ent_usg_pv_df['end_dt'].notnull())


print('---------------------------------------------------------------------------------------------------------')
print('---------------------------------------------------------------------------------------------------------')
print('Number of total batch records submitted (including any duplicate submissions): {}'.format(total_count))
print('\n')

print('---------------------------------------------------------------------------------------------------------')
print('---------------------------------------------------------------------------------------------------------')
print('Overall Results Before Dropping Duplicate Batch Entries (Duplicate Entries May Be Counted)')
print('---------------------------------------------------------------------------------------------------------')
print('---------------------------------------------------------------------------------------------------------')
print('Number of total records with entity_comm_at entries: {}'.format(combined_ent_df.shape[0]))
print('Number of total records with null entity_comm_at ent_dt: {}'.format(total_no_end))
print('Number of total records with entity_comm_at ent_dt present: {}'.format(total_w_end))
print('\n')
print('Number of total records with entity_comm_usg_at entries: {}'.format(combined_ent_usg_df.shape[0]))
print('Number of total records with null entity_comm_usg_at ent_dt: {}'.format(total_no_end_usg))
print('Number of total records with entity_comm_usg_at ent_dt present: {}'.format(total_w_end_usg))
print('\n')
print('Number of total records with entity_comm_usg_at PV entries: {}'.format(combined_ent_usg_pv_df.shape[0]))
print('Number of total records with null entity_comm_usg_at PV ent_dt: {}'.format(total_no_end_usg_pv))
print('Number of total records with entity_comm_usg_at ent_dt PV present: {}'.format(total_w_end_usg_pv))
print('\n')

uniq_comb_ent_df = combined_ent_df.drop_duplicates()
uniq_no_end = sum(uniq_comb_ent_df['end_dt'].isna())
uniq_w_end = sum(uniq_comb_ent_df['end_dt'].notnull())

uniq_anlys_out_file = support_dir + start_time_str + '_Uniq_EntComm_Data.csv'
uniq_comb_ent_df.to_csv(uniq_anlys_out_file, index = False, header = True)

uniq_comb_ent_usg_df = combined_ent_usg_df.drop_duplicates()
uniq_no_end_usg = sum(uniq_comb_ent_usg_df['end_dt'].isna())
uniq_w_end_usg = sum(uniq_comb_ent_usg_df['end_dt'].notnull())

uniq_usg_anlys_out_file = support_dir + start_time_str + '_Uniq_EntCommUsg_Data.csv'
uniq_comb_ent_usg_df.to_csv(uniq_usg_anlys_out_file, index = False, header = True)

uniq_comb_ent_usg_pv_df = combined_ent_usg_pv_df.drop_duplicates()
uniq_no_end_usg_pv = sum(uniq_comb_ent_usg_pv_df['end_dt'].isna())
uniq_w_end_usg_pv = sum(uniq_comb_ent_usg_pv_df['end_dt'].notnull())

uniq_usg_pv_anlys_out_file = support_dir + start_time_str + '_Uniq_EntCommUsgPreferred_Data.csv'
uniq_comb_ent_usg_pv_df.to_csv(uniq_usg_pv_anlys_out_file, index = False, header = True)


print('---------------------------------------------------------------------------------------------------------')
print('---------------------------------------------------------------------------------------------------------')
print('Overall Results After Dropping Duplicate Batch Entries (Actual Number Of Records End Dated)')
print('---------------------------------------------------------------------------------------------------------')
print('---------------------------------------------------------------------------------------------------------')
print('Number of unique records with entity_comm_at entries: {}'.format(uniq_comb_ent_df.shape[0]))
print('Number of unique records with null entity_comm_at ent_dt: {}'.format(uniq_no_end))
print('Number of unique records with entity_comm_at ent_dt present: {}'.format(uniq_w_end))
print('\n')
print('Number of unique records with entity_comm_usg_at entries: {}'.format(uniq_comb_ent_usg_df.shape[0]))
print('Number of unique records with null entity_comm_usg_at ent_dt: {}'.format(uniq_no_end_usg))
print('Number of unique records with entity_comm_usg_at ent_dt present: {}'.format(uniq_w_end_usg))
print('\n')
print('Number of unique records with entity_comm_usg_at PV entries: {}'.format(uniq_comb_ent_usg_pv_df.shape[0]))
print('Number of unique records with null entity_comm_usg_at PV ent_dt: {}'.format(uniq_no_end_usg_pv))
print('Number of unique records with entity_comm_usg_atPV  ent_dt present: {}'.format(uniq_w_end_usg_pv))
print('\n')

# create counts of different source types of DPC PPD entries to save
comb_kb_src_cnt = uniq_comb_ent_df.sort_values(['src_cat_code']).groupby(['src_cat_code']).size().reset_index()
comb_kb_src_cnt = comb_kb_src_cnt.rename(columns = {0:'count'})

# Save source count information
kb_source_out_file = anlys_out_dir + start_time_str + '_Uniq_KB_Source_Counts.xlsx'
writer = pd.ExcelWriter(kb_source_out_file, engine = 'xlsxwriter')
comb_kb_src_cnt.to_excel(writer, sheet_name = 'combined_kb_source_cnt', index = False, header = 0)
writer.save()

num_rows = comb_kb_src_cnt.shape[0] + 1
num_cols = comb_kb_src_cnt.shape[1] + 1
pd.set_option('max_rows', num_rows)
pd.set_option('max_columns', num_cols)

print('---------------------------------------------------------------------------------------------------------')
print('---------------------------------------------------------------------------------------------------------')
print('Overall Source Counts Source Counts (Using Unique Entity_Comm Records)')
print('---------------------------------------------------------------------------------------------------------')
print('---------------------------------------------------------------------------------------------------------')
print('Known Bad Source Count:')
print(comb_kb_src_cnt)

sys.stdout = old_stdout
log_file.close()

















