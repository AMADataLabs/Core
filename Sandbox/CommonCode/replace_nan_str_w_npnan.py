# Kari Palmier    9/30/19    Created
#
#############################################################################
import os
import sys

import numpy as np

import datalabs.curate.dataframe as df

def replace_nan_str_w_npnan(data_df):   
    
    data_df = df.upper_values(data_df)
    
    col_names = list(data_df.columns.values)
    for name in col_names:
        data_df[name] = data_df[name].apply(lambda x: np.nan if x == 'NAN' else x)
        
    return data_df
