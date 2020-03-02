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
from select_files import select_files
from exclude_phone_samples import exclude_phone_samples
from get_ddb_logins import get_ddb_logins
from get_aims_db_tables import get_pe_description, get_aims_connection
from capitalize_column_names import capitalize_column_names

import warnings
warnings.filterwarnings("ignore")

sample_vars = ['ME', 'FIRST_NAME', 'MIDDLE_NAME', 'LAST_NAME', 'SUFFIX',
               'POLO_MAILING_LINE_1', 'POLO_MAILING_LINE_2', 'POLO_CITY',
               'POLO_STATE', 'POLO_ZIP', 'TELEPHONE_NUMBER', 'PRIM_SPEC_CD',
               'DESCRIPTION', 'PE_CD', 'FAX_NUMBER']

init_ppd_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\PPD\\'
init_vt_response_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Vertical_Trail\\Response\\'
int_vt_orig_batch_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Vertical_Trail\\Batches_To_VT\\'
init_survey_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Survey_Samples\\Vertical_Trail\\'

# Get files needed
ddb_info_file = filedialog.askopenfilename(initialdir="C:\\",
                                           title="Choose txt file with database login information...")

vt_response_file = filedialog.askopenfilename(initialdir=init_vt_response_dir,
                                              title="Choose Vertical Trail response file...")

int_vt_batch_file = filedialog.askopenfilename(initialdir=int_vt_orig_batch_dir,
                                               title="Choose internal version of the file sent to Vertical Trail...")

ppd_file = filedialog.askopenfilename(initialdir=init_ppd_dir,
                                      title="Choose latest PPD CSV file...")

survey_out_dir = filedialog.askdirectory(initialdir=init_survey_dir,
                                         title="Choose directory to save survey sample output...")
survey_out_dir = survey_out_dir.replace("/", "\\")
survey_out_dir += "\\"


init_exclude_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Survey_Samples\\'
print('ME and phone numbers from all past month and other current month sample files must be excluded.')
print('The following prompts will select each file to exclude.')
exclude_list = select_files(init_exclude_dir, 'Select sample file(s) to exclude')

sample_str = input('Enter the sample size (all = all samples in bin): ')
if sample_str.lower() == 'all' or not(sample_str.isnumeric()):
    sample_size = 'all'
else:
    sample_size = int(sample_str)
print('\n')

current_time = datetime.datetime.now()
start_time_str = current_time.strftime("%Y-%m-%d")

vt_resp_base_file = vt_response_file.replace("/", "\\")
slash_ndx = [i for i in range(len(vt_resp_base_file)) if vt_resp_base_file.startswith('\\', i)]
base_anyls_name = vt_resp_base_file[slash_ndx[-1]+1:]
dot_ndx = base_anyls_name.find('.')


# Get ddb login information
ddb_login_dict = get_ddb_logins(ddb_info_file)

if 'AIMS' not in ddb_login_dict.keys():
    print('AIMS login information not present.')
    sys.exit()
   
# Connect to AIMS production database
AIMS_conn = get_aims_connection(ddb_login_dict['AIMS']['username'], ddb_login_dict['AIMS']['password'])

pe_desc_df = get_pe_description(AIMS_conn)

AIMS_conn.close()

pe_desc_df = pe_desc_df.rename(columns={'description': 'DESCRIPTION'})


# Read in VT response data
if vt_response_file.find('.csv') >= 0:
    vt_resp_df = pd.read_csv(vt_response_file, delimiter=",", index_col=None, header=0, dtype=str)
else:  
    vt_resp_df = pd.read_excel(vt_response_file, index_col=None, header=0, dtype=str)
vt_resp_df = capitalize_column_names(vt_resp_df)
print('Vertical Trail response Size: {}'.format(len(vt_resp_df)))

# Read in VT internal version of batch data
if int_vt_batch_file.find('.csv') >= 0:
    vt_int_batch_df = pd.read_csv(int_vt_batch_file, delimiter=",", index_col=None, header=0, dtype=str)
else:
    vt_int_batch_df = pd.read_excel(int_vt_batch_file, index_col=None, header=0, dtype=str)
if 'me' in list(vt_int_batch_df.columns.values):
    vt_int_batch_df = vt_int_batch_df.rename(columns={'me': 'entity_me'})
vt_int_batch_df = capitalize_column_names(vt_int_batch_df)
if 'DESCRIPTION' in list(vt_int_batch_df.columns.values):
    vt_int_batch_df = vt_int_batch_df.rename(columns={'DESCRIPTION': 'SPEC_DESCRIPTION'})

print('Internal version size: {}'.format(len(vt_int_batch_df)))

# Read PPD and find only non-null TELEPHONE NUMBER entries
ppd_df = pd.read_csv(ppd_file, delimiter=",", index_col=None, header=0, dtype=str)
ppd_df = capitalize_column_names(ppd_df)
ppd_null_df = ppd_df[ppd_df['TELEPHONE_NUMBER'].isna()]

# Convert med school year to string without decimal point 
vt_resp_df['MEDSCHOOL_GRAD_YEAR'] = \
    vt_resp_df['MEDSCHOOL_GRAD_YEAR'].apply(lambda x: x[0:4] if ((x is not None) and (~np.isnan(float(x)))) else x)

resp_w_info_df = vt_resp_df.merge(vt_int_batch_df, how='inner', on=['LAST_NAME', 'FIRST_NAME',
                                                                    'MEDSCHOOL_GRAD_YEAR',
                                                                    'LIC_STATE'])


remove_current = int(input('Remove response records for MEs which already have numbers in PPD? (1=yes, 0=no)'))
if remove_current == 1:
    resp_ppd_df = resp_w_info_df.merge(ppd_null_df, how='inner', on='ME')
else:
    resp_ppd_df = resp_w_info_df

resp_ppd_cols = resp_ppd_df.columns.values
for name in sample_vars:
    merge_name = name + '_y'
    if merge_name in resp_ppd_cols:
        if name in resp_ppd_cols:
            resp_ppd_df = resp_ppd_df.drop([name], axis=1)
            
        resp_ppd_df = resp_ppd_df.rename(columns={merge_name: name})


resp_ppd_df = resp_ppd_df.merge(pe_desc_df, how='inner',
                                left_on='PE_CD',  right_on='present_emp_cd')

col_names = resp_ppd_df.columns.values
for name in col_names:
    none_ndx = resp_ppd_df[name] == 'None'
    resp_ppd_df.loc[none_ndx, name] = np.nan

print(resp_ppd_df.columns.values)
resp_ppd_df = resp_ppd_df[resp_ppd_df['OFFICE 1 PHONE NUMBER - GENERAL'].notnull()]


# Get list of good and bad phone numbers
print('Bad Phone Number Filtering Results')
print('----------------------------------')
resp_phone_present_df = resp_ppd_df[resp_ppd_df['OFFICE 1 PHONE NUMBER - GENERAL'].notnull()]
bad_phone_df, good_phone_df = get_good_bad_phones(resp_phone_present_df, 'OFFICE 1 PHONE NUMBER - GENERAL')


good_phone_df = good_phone_df.drop(['TELEPHONE_NUMBER', 'FAX_NUMBER'], axis=1)
good_phone_df = good_phone_df.rename(columns={'OFFICE 1 PHONE NUMBER - GENERAL': 'TELEPHONE_NUMBER',
                                              'OFFICE 1 FAX NUMBER': 'FAX_NUMBER'})
sample_df = good_phone_df[sample_vars]
sample_df = exclude_phone_samples(sample_df, exclude_list, 'ME', 'TELEPHONE_NUMBER')


if sample_size == 'all':
    sample_df = sample_df
else:
    print('Sampling {} from population of {}'.format(sample_size, len(sample_df)))
    sample_df = sample_df.sample(sample_size)

sample_df.fillna('', inplace=True)
sample_df.replace('nan', '', inplace=True)

save_file = survey_out_dir + start_time_str + '_VT_VerificationSample.xlsx'
writer = pd.ExcelWriter(save_file, engine='xlsxwriter')
sample_df.to_excel(writer, index=None, header=True)
writer.save()
