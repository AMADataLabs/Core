# Kari Palmier    Created 8/20/19
#
#############################################################################
import os
import sys

import pandas as pd

import datalabs.curate.dataframe  # pylint: disable=unused-import


def exclude_phone_samples(curr_sample_df, exclude_list, me_var_name, phone_var_name):
    
    if exclude_list == []:
        return curr_sample_df

    curr_sample_df = curr_sample_df.datalabs.rename_in_upper_case()
    phone_var_name = phone_var_name.upper()
    curr_sample_df[me_var_name] = curr_sample_df[me_var_name].astype('str')
    curr_sample_df[phone_var_name] = curr_sample_df[phone_var_name].astype('str')
    curr_sample_df['me_phone'] = curr_sample_df[me_var_name] + '-' + curr_sample_df[phone_var_name]
    
    for i in range(len(exclude_list)):
        
        file = exclude_list[i]
        
        if file.find('.csv') >= 0:
            temp_df = pd.read_csv(file, delimiter = ",", index_col = None, header = 0, dtype = str)
        else:
            temp_df = pd.read_excel(file, index_col = None, header = 0, dtype = str)
        
        temp_df = temp_df.datalabs.rename_in_upper_case()
                    
        temp_df['me_phone'] = temp_df[me_var_name] + '-' + temp_df[phone_var_name]
        
        curr_sample_df = curr_sample_df[~curr_sample_df['me_phone'].isin(temp_df['me_phone'])]
        
    curr_sample_df = curr_sample_df.drop(['me_phone'], axis = 1)
    
    return curr_sample_df

        
        
