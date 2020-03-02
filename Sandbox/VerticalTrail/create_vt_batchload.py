# Kari Palmier    Created 8/14/19
#
#############################################################################
import pandas as pd
from tkinter import filedialog
import datetime
import numpy as np

# Get path of general (common) code and add it to the python path variable
import sys
import os
curr_path = os.path.abspath(__file__)
slash_ndx = [i for i in range(len(curr_path)) if curr_path.startswith('\\', i)]
base_path = curr_path[:slash_ndx[-2]+1]
gen_path = base_path + 'Common_Code\\'
sys.path.insert(0, gen_path)

from filter_bad_phones import get_good_bad_phones
from create_batch_loads import create_phone_append, create_fax_append
from capitalize_column_names import capitalize_column_names


import warnings
warnings.filterwarnings("ignore")

init_ppd_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\PPD\\'
init_vt_response_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Vertical_Trail\\Response\\'
init_vt_sent_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Vertical_Trail\\Batches_To_VT\\'
int_vt_orig_batch_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Vertical_Trail\\Batches_To_VT\\'
init_anlys_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Vertical_Trail\Analysis\\'
init_batch_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\IT_BatchLoads\\Vertical_Trail\\'

vt_response_file = filedialog.askopenfilename(initialdir=init_vt_response_dir,
                                              title="Choose Vertical Trail response file...")

int_vt_batch_file = filedialog.askopenfilename(initialdir=int_vt_orig_batch_dir,
                                               title="Choose internal version of the file sent to Vertical Trail...")

ppd_file = filedialog.askopenfilename(initialdir=init_ppd_dir,
                                      title="Choose latest PPD CSV file...")

anlys_out_dir = filedialog.askdirectory(initialdir=init_anlys_dir,
                                        title="Choose directory to save analysis output...")
anlys_out_dir = anlys_out_dir.replace("/", "\\")
anlys_out_dir += "\\"

support_dir = anlys_out_dir + 'Support\\'
if not os.path.exists(support_dir):
    os.mkdir(support_dir)

batch_out_dir = filedialog.askdirectory(initialdir=init_batch_dir,
                                        title="Choose directory to save batch file output...")
batch_out_dir = batch_out_dir.replace("/", "\\")
batch_out_dir += "\\"


current_time = datetime.datetime.now()
start_time_str = current_time.strftime("%Y-%m-%d")

vt_resp_base_file = vt_response_file.replace("/", "\\")
slash_ndx = [i for i in range(len(vt_resp_base_file)) if vt_resp_base_file.startswith('\\', i)]
base_anyls_name = vt_resp_base_file[slash_ndx[-1]+1:]
dot_ndx = base_anyls_name.find('.')

vt_resp_w_info_file = support_dir + base_anyls_name[:dot_ndx] + '_All_Info.csv'
vt_good_phone_file = support_dir + base_anyls_name[:dot_ndx] + '_Good_Phone_Info.csv'
vt_bad_phone_file = support_dir + base_anyls_name[:dot_ndx] + '_Bad_Phone_Info.csv'
vt_good_fax_file = support_dir + base_anyls_name[:dot_ndx] + '_Good_Fax_Info.csv'
vt_bad_fax_file = support_dir + base_anyls_name[:dot_ndx] + '_Bad_Fax_Info.csv'

batch_phone_file = batch_out_dir + 'HSG_PHYS_WEBVRTR_PHONE_' + start_time_str + '.csv'
batch_fax_file = batch_out_dir + 'HSG_PHYS_WEBVRTR_FAX_' + start_time_str + '.csv'

# Create log file
old_stdout = sys.stdout
log_filename = anlys_out_dir + base_anyls_name[:dot_ndx] + '_Analysis_Log' + '.txt'
log_file = open(log_filename, "w")
sys.stdout = log_file


# Read in VT response data
if vt_response_file.find('.csv') >= 0:
    vt_resp_df = pd.read_csv(vt_response_file, delimiter=",", index_col=None, header=0, dtype=str)
else:
    vt_resp_df = pd.read_excel(vt_response_file, index_col=None, header=0, dtype=str)
vt_resp_df = capitalize_column_names(vt_resp_df)
    
# Read in VT internal version of batch data
if int_vt_batch_file.find('.csv') >= 0:
    vt_int_batch_df = pd.read_csv(int_vt_batch_file, delimiter=",", index_col=None, header=0, dtype=str)
else:
    vt_int_batch_df = pd.read_excel(int_vt_batch_file, index_col=None, header=0, dtype=str)
if 'me' in list(vt_int_batch_df.columns.values):
    vt_int_batch_df = vt_int_batch_df.rename(columns={'me': 'entity_me'})
vt_int_batch_df = capitalize_column_names(vt_int_batch_df)


# Read PPD and find only non-null TELEPHONE NUMBER entries
ppd_df = pd.read_csv(ppd_file, delimiter=",", index_col=None, header=0, dtype=str)
ppd_null_df = ppd_df[ppd_df['TELEPHONE_NUMBER'].isna()]


resp_cols = list(vt_resp_df.columns.values)
if 'RPV_CONNECTED/-75' in resp_cols:
    na_ndx = (vt_resp_df['RPV_CONNECTED/-75'] == '#N/A') | vt_resp_df['RPV_CONNECTED/-75'].isna() | \
              (vt_resp_df['RPV_CONNECTED/-75'] == 'None')
    vt_resp_df = vt_resp_df[~na_ndx]      
    
    one_ndx = (vt_resp_df['RPV_CONNECTED/-75'] == 1) | (vt_resp_df['RPV_CONNECTED/-75'] == '1')
    vt_resp_df = vt_resp_df[one_ndx]      
    

# Convert med school year to string without decimal point 
vt_resp_df['MEDSCHOOL_GRAD_YEAR'] = \
    vt_resp_df['MEDSCHOOL_GRAD_YEAR'].apply(lambda x: x[0:4] if ((x is not None) and (~np.isnan(float(x)))) else x)

resp_w_info_df = vt_resp_df.merge(vt_int_batch_df, how='inner', on=['LAST_NAME', 'FIRST_NAME',
                                                                     'MEDSCHOOL_GRAD_YEAR',
                                                                     'LIC_STATE'])

col_names = resp_w_info_df.columns.values
for name in col_names:
    none_ndx = resp_w_info_df[name] == 'None'
    resp_w_info_df.loc[none_ndx, name] = np.nan
    
    
resp_ppd_df = resp_w_info_df.merge(ppd_null_df, how='inner', on='ME')


print('----------------------------------------------------------------------------')
print('Vertical Trail Bad Number Filtering Results')
print('----------------------------------------------------------------------------')
print('\n')

# Get list of good and bad phone numbers
print('Bad Phone Number Filtering Results')
print('----------------------------------')
resp_phone_present_df = resp_ppd_df[resp_ppd_df['OFFICE 1 PHONE NUMBER - GENERAL'].notnull()]
bad_phone_df, good_phone_df = get_good_bad_phones(resp_phone_present_df, 'OFFICE 1 PHONE NUMBER - GENERAL')
phone_add_batch = create_phone_append(good_phone_df, 'ME', 'OFFICE 1 PHONE NUMBER - GENERAL', 'WEBVRTR')

print('\n')
print('Bad Fax Number Filtering Results')
print('----------------------------------')
resp_fax_present_df = resp_ppd_df[resp_ppd_df['OFFICE 1 FAX NUMBER'].notnull()]
bad_fax_df, good_fax_df = get_good_bad_phones(resp_fax_present_df, 'OFFICE 1 FAX NUMBER')
fax_add_batch = create_fax_append(good_fax_df, 'ME', 'OFFICE 1 FAX NUMBER', 'WEBVRTR')

# Save off files with data
resp_w_info_df.to_csv(vt_resp_w_info_file, index=False, header=True)
good_phone_df.to_csv(vt_good_phone_file, index=False, header=True)
bad_phone_df.to_csv(vt_bad_phone_file, index=False, header=True)
good_fax_df.to_csv(vt_good_fax_file, index=False, header=True)
bad_fax_df.to_csv(vt_bad_fax_file, index=False, header=True)

phone_add_batch.to_csv(batch_phone_file, index=False, header=True)
fax_add_batch.to_csv(batch_fax_file, index=False, header=True)

print('\n')
print('----------------------------------------------------------------------------')
print('Vertical Trail Results Summary')
print('----------------------------------------------------------------------------')

print('Number of samples sent to Vertical  Trail: {}'.format(vt_int_batch_df.shape[0]))   
print('Number of samples received from Vertical Trail: {}'.format(vt_resp_df.shape[0]))
print('Number of samples received with null phones in current PPD: {}'.format(resp_ppd_df.shape[0]))
 
print('\n')
print('Phone Results')
print('-------------')    
print('Number of samples from Vertical Trail with phones: {}'.format(\
      resp_w_info_df[resp_w_info_df['OFFICE 1 PHONE NUMBER - GENERAL'].notnull()].shape[0]))
print('\n')
print('--- PPD Null Entry Phone Analysis ---')
print('Number of samples from Vertical Trail with phones: {}'.format(resp_phone_present_df.shape[0]))
print('Number of Vertical Trail responses that had bad phones: {}'.format(bad_phone_df.shape[0]))
print('Number of Vertical Trail phones to be batch loaded: {}'.format(phone_add_batch.shape[0]))
print('\n')

print('Fax Results')
print('-----------')    
print('Number of samples from Vertical Trail with faxes: {}'.format(\
      resp_w_info_df[resp_w_info_df['OFFICE 1 FAX NUMBER'].notnull()].shape[0]))
print('\n')
print('--- PPD Null Entry Phone Analysis ---')
print('Number of samples from Vertical Trail with faxes: {}'.format(resp_fax_present_df.shape[0]))
print('Number of Vertical Trail responses that had bad faxes: {}'.format(bad_fax_df.shape[0]))
print('Number of Vertical Trail faxes to be batch loaded: {}'.format(fax_add_batch.shape[0]))
print('\n')

vt_resp_email_df = resp_w_info_df[resp_w_info_df['OFFICE 1 EMAIL'].notnull()]

print('Email Results')
print('-----------')    
print('Number of samples from Vertical Trail with emails: {}'.format(vt_resp_email_df.shape[0]))

sys.stdout = old_stdout
log_file.close()












