# Kari Palmier    Created 8/8/19
#
#############################################################################

import pandas as pd

import warnings
warnings.filterwarnings("ignore")


# 8885785910 was provided from Humach via Derek on 8/5/2019
# 2147483647 was found to be bad through analysis and calling the number on 8/7/2019
known_bad_numbers = ['8885785910', '2147483647', '9999999999']

bad_area_starts = ['0', '1']
bad_area_codes = ['211', '311', '411', '511', '611', '711', '811', '911', '370', '371', '372', '373', 
                  '374', '375', '376', '377', '378', '379', '960', '961', '962', '963', '964', '965',
                  '966', '967', '968', '969']
bad_prefix_starts = ['0', '1']
bad_prefixes = ['555', '211', '311', '411', '511', '611', '711', '811', '911', '958', '959']


# This function is for possible future usage.  Did not want to restrict area codes too much
# since new area codes are still being created
def get_area_code_info(area_code_file):
    
    #area_code_file = 'C:\\AMA Sandbox\\Common Code\\area_codes.csv'
    
    area_df = pd.read_csv(area_code_file, delimiter = ",", index_col = None, header = 0, dtype = 'object')
    
    bad_ndx = area_df['in_use'] == '0'
    bad_area_code_df = area_df[bad_ndx]
    bad_area_codes = list(bad_area_code_df['area_code'])
    
    good_area_code_df = area_df[~bad_ndx]
    good_area_codes = list(good_area_code_df['area_code'])
    
    return bad_area_codes, good_area_codes
   

def get_good_bad_phones(orig_df, phone_var_name):
    
    data_df = orig_df[orig_df[phone_var_name].notnull()]
    
    data_df[phone_var_name] = data_df[phone_var_name].astype('str')
    
    data_df['area_code'] = data_df[phone_var_name].apply(lambda x: x[0:3])
    data_df['area_code_start'] = data_df[phone_var_name].apply(lambda x: x[0:1])
    data_df['prefix'] = data_df[phone_var_name].apply(lambda x: x[3:6])
    data_df['prefix_start'] = data_df['prefix'].apply(lambda x: x[0:1])
    
    kb_ndx = data_df[phone_var_name].isin(known_bad_numbers)
    
    kb_df = data_df[kb_ndx]
    not_kb_df = data_df[~kb_ndx]
    
    bad_area_start_ndx = not_kb_df['area_code_start'].isin(bad_area_starts)
    bad_area_start_df = not_kb_df[bad_area_start_ndx]
    good_area_start_df = not_kb_df[~bad_area_start_ndx]
    
    #bad_area_codes, good_area_codes = get_area_code_info()
    bad_area_ndx = good_area_start_df['area_code'].isin(bad_area_codes)
    bad_area_df = good_area_start_df[bad_area_ndx]
    good_area_df = good_area_start_df[~bad_area_ndx]
       
    bad_prefix_start_ndx = good_area_df['prefix_start'].isin(bad_prefix_starts)
    bad_prefix_start_df = good_area_df[bad_prefix_start_ndx]
    good_prefix_start_df = good_area_df[~bad_prefix_start_ndx]

    bad_prefix_ndx = good_prefix_start_df['prefix'].isin(bad_prefixes)
    bad_prefix_df = good_prefix_start_df[bad_prefix_ndx]
    good_prefix_df = good_prefix_start_df[~bad_prefix_ndx]
    
    bad_df = bad_prefix_df[:]
    bad_df = pd.concat([bad_df, bad_prefix_start_df], ignore_index = True)
    bad_df = pd.concat([bad_df, bad_area_df], ignore_index = True)
    bad_df = pd.concat([bad_df, bad_area_start_df], ignore_index = True)
    bad_df = pd.concat([bad_df, kb_df], ignore_index = True)
    bad_df = bad_df.drop(['area_code', 'area_code_start', 'prefix', 'prefix_start'], axis=1)

    good_df = good_prefix_df[:]
    good_df = good_df.drop(['area_code', 'area_code_start', 'prefix', 'prefix_start'], axis=1)
    
    print('\n')
    print('Number of known bad numbers: {}'.format(kb_df.shape[0]))
    print('Number of area codes starting with 0 or 1 (bad): {}'.format(bad_area_start_df.shape[0]))
    print('Number of numbers with bad area codes (not including 0 and 1 starts): {}'.format(bad_area_df.shape[0]))
    print('Number of prefixes starting with 0 or 1 (bad): {}'.format(bad_prefix_start_df.shape[0]))
    print('Number of numbers with bad prefixes (not including 0 and 1 starts): {}'.format(bad_prefix_df.shape[0]))
    
    print('\n')
    print('Total number of original entries: {}'.format(orig_df.shape[0]))    
    print('Number of original entries with phone numbers: {}'.format(data_df.shape[0]))
    print('Number of bad phone entries: {}'.format(bad_df.shape[0]))    
    print('Number of good phone entries: {}'.format(good_df.shape[0]))    
    
    return bad_df, good_df
     
